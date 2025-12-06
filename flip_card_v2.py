"""
FLIP CARD V2.2 - Professional with Real Equations
=================================================
Pure CSS flip animation with actual component breakdown.

Back of card shows:
- Formula with REAL numbers from extraction
- Brief actionable insight
- Color-coded benchmark status
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, List, Optional
import pandas as pd
import hashlib

# ============================================================================
# METRIC DEFINITIONS WITH COMPONENT KEYS
# ============================================================================

METRIC_CONFIG = {
    "PE_Ratio": {
        "name": "P/E Ratio",
        "formula_template": "{price} ÷ {eps}",
        "components": ["price", "eps"],
        "insight": "Investor sentiment per $1 earnings",
        "benchmark": (15, 25),
        "higher_is_better": False,
        "valid_range": (0, 500),
        "unit": "x"
    },
    "ROE": {
        "name": "ROE",
        "formula_template": "{net_income} ÷ {equity}",
        "components": ["net_income", "equity"],
        "insight": "Profit per shareholder dollar",
        "benchmark": (10, 20),
        "higher_is_better": True,
        "valid_range": (-100, 200),
        "unit": "%"
    },
    "Debt_to_Equity": {
        "name": "D/E Ratio",
        "formula_template": "{total_debt} ÷ {equity}",
        "components": ["total_debt", "equity"],
        "insight": "Leverage risk. <1 is conservative",
        "benchmark": (0.5, 1.5),
        "higher_is_better": False,
        "valid_range": (0, 50),
        "unit": "x"
    },
    "Gross_Margin": {
        "name": "Gross Margin",
        "formula_template": "({revenue} - {cogs}) ÷ {revenue}",
        "components": ["revenue", "cogs", "gross_profit"],
        "insight": "Pricing power. >40% is strong",
        "benchmark": (30, 50),
        "higher_is_better": True,
        "valid_range": (-50, 100),
        "unit": "%"
    },
    "Net_Margin": {
        "name": "Net Margin",
        "formula_template": "{net_income} ÷ {revenue}",
        "components": ["net_income", "revenue"],
        "insight": "Bottom line per $1 revenue",
        "benchmark": (5, 15),
        "higher_is_better": True,
        "valid_range": (-100, 100),
        "unit": "%"
    },
    "Current_Ratio": {
        "name": "Current Ratio",
        "formula_template": "{current_assets} ÷ {current_liab}",
        "components": ["current_assets", "current_liab"],
        "insight": "Short-term liquidity. >1.5 comfortable",
        "benchmark": (1.0, 2.0),
        "higher_is_better": True,
        "valid_range": (0, 20),
        "unit": "x"
    },
    "FCF_Yield": {
        "name": "FCF Yield",
        "formula_template": "{fcf} ÷ {market_cap}",
        "components": ["fcf", "market_cap"],
        "insight": "Cash generation vs price. >5% attractive",
        "benchmark": (3, 8),
        "higher_is_better": True,
        "valid_range": (-50, 50),
        "unit": "%"
    },
    "Dividend_Yield": {
        "name": "Div. Yield",
        "formula_template": "{annual_div} ÷ {price}",
        "components": ["annual_div", "price"],
        "insight": "Income return. >4% is high yield",
        "benchmark": (2, 5),
        "higher_is_better": True,
        "valid_range": (0, 20),
        "unit": "%"
    },
    "Beta": {
        "name": "Beta",
        "formula_template": "Cov(Stock,Mkt) ÷ Var(Mkt)",
        "components": [],
        "insight": "Volatility vs market. >1 = more volatile",
        "benchmark": (0.8, 1.2),
        "higher_is_better": None,
        "valid_range": (-2, 5),
        "unit": ""
    },
    "EPS": {
        "name": "EPS",
        "formula_template": "{net_income} ÷ {shares}",
        "components": ["net_income", "shares"],
        "insight": "Earnings per share",
        "benchmark": (1, 10),
        "higher_is_better": True,
        "valid_range": (-100, 1000),
        "unit": "$"
    },
    "current_price": {
        "name": "Price",
        "formula_template": "Market Price",
        "components": [],
        "insight": "Compare to intrinsic value",
        "benchmark": None,
        "higher_is_better": None,
        "valid_range": (0.01, 100000),
        "unit": "$"
    },
    "market_cap": {
        "name": "Market Cap",
        "formula_template": "{price} × {shares}",
        "components": ["price", "shares"],
        "insight": "Company size. Large cap >$10B",
        "benchmark": None,
        "higher_is_better": None,
        "valid_range": (1e6, 1e14),
        "unit": "$"
    }
}


def fmt_num(val: Any, short: bool = True) -> str:
    """Format number for display in equation."""
    if val is None:
        return "N/A"
    try:
        num = float(val)
        if pd.isna(num):
            return "N/A"
        if short:
            if abs(num) >= 1e12:
                return f"${num/1e12:.1f}T"
            elif abs(num) >= 1e9:
                return f"${num/1e9:.1f}B"
            elif abs(num) >= 1e6:
                return f"${num/1e6:.1f}M"
            elif abs(num) >= 1000:
                return f"${num/1000:.1f}K"
            else:
                return f"${num:.2f}"
        return f"{num:.2f}"
    except:
        return "N/A"


def get_color(value: float, metric_key: str) -> str:
    """Get color based on benchmark."""
    if value is None:
        return "#6b7280"  # Gray
    
    config = METRIC_CONFIG.get(metric_key, {})
    benchmark = config.get("benchmark")
    higher_is_better = config.get("higher_is_better")
    
    if benchmark is None or higher_is_better is None:
        return "#60a5fa"  # Blue neutral
    
    low, high = benchmark
    
    if higher_is_better:
        if value >= high:
            return "#10b981"  # Green
        elif value <= low:
            return "#ef4444"  # Red
        else:
            return "#f59e0b"  # Yellow
    else:
        if value <= low:
            return "#10b981"  # Green
        elif value >= high:
            return "#ef4444"  # Red
        else:
            return "#f59e0b"  # Yellow


def format_value(value: Any, unit: str, metric_key: str) -> str:
    """Format the main display value."""
    if value is None:
        return "N/A"
    
    try:
        num = float(value)
        if pd.isna(num):
            return "N/A"
    except:
        return "N/A"
    
    # Handle decimal-to-percentage conversion
    if unit == "%" and metric_key in ["ROE", "Gross_Margin", "Net_Margin", "FCF_Yield", "Dividend_Yield"]:
        if abs(num) < 1:
            num = num * 100
    
    # Handle D/E stored as percentage
    if metric_key == "Debt_to_Equity" and num > 10:
        num = num / 100
    
    # Format
    if unit == "$":
        if abs(num) >= 1e12:
            return f"${num/1e12:.2f}T"
        elif abs(num) >= 1e9:
            return f"${num/1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"${num/1e6:.2f}M"
        else:
            return f"${num:.2f}"
    elif unit == "%":
        return f"{num:.2f}%"
    elif unit == "x":
        return f"{num:.2f}x"
    else:
        return f"{num:.2f}"


def build_equation_html(metric_key: str, components: Dict) -> str:
    """Build the actual equation with real numbers."""
    config = METRIC_CONFIG.get(metric_key, {})
    template = config.get("formula_template", "")
    
    if not template:
        return ""
    
    # Replace placeholders with actual values
    equation = template
    for comp_name in config.get("components", []):
        comp_val = components.get(comp_name)
        formatted = fmt_num(comp_val)
        equation = equation.replace("{" + comp_name + "}", formatted)
    
    # If any placeholders remain, they weren't found
    if "{" in equation:
        return template  # Return template without values
    
    return equation


def create_flip_card(
    metric_key: str,
    value: Any,
    label: str,
    components: Dict,
    card_id: str = None
) -> str:
    """Create a flip card with real equation on back."""
    
    if card_id is None:
        card_id = hashlib.md5(f"{metric_key}_{label}".encode()).hexdigest()[:8]
    
    config = METRIC_CONFIG.get(metric_key, {})
    unit = config.get("unit", "")
    insight = config.get("insight", "")
    benchmark = config.get("benchmark")
    
    # Format value and get color
    formatted = format_value(value, unit, metric_key)
    
    # Get actual numeric for color calculation
    try:
        num_val = float(value) if value else None
        if num_val and unit == "%" and abs(num_val) < 1:
            num_val = num_val * 100
        if metric_key == "Debt_to_Equity" and num_val and num_val > 10:
            num_val = num_val / 100
    except:
        num_val = None
    
    color = get_color(num_val, metric_key)
    
    # Build equation with actual numbers
    equation = build_equation_html(metric_key, components)
    
    # Benchmark text
    bench_html = ""
    if benchmark:
        low, high = benchmark
        bench_html = f"<span style='color:#6e7681;font-size:0.55rem;'>Benchmark: {low}-{high}{unit}</span>"
    
    html = f"""
    <style>
        .fc-{card_id} {{
            perspective: 800px;
            width: 100%;
            height: 85px;
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
        }}
        .fc-inner-{card_id} {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }}
        .fc-{card_id}:hover .fc-inner-{card_id} {{
            box-shadow: 0 6px 20px rgba(0,0,0,0.25);
        }}
        .fc-{card_id}.flipped .fc-inner-{card_id} {{
            transform: rotateY(180deg);
        }}
        .fc-front-{card_id}, .fc-back-{card_id} {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 8px 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            border-left: 3px solid {color};
            background: linear-gradient(145deg, #1a2332 0%, #0d1117 100%);
        }}
        .fc-back-{card_id} {{
            transform: rotateY(180deg);
        }}
        .fc-lbl-{card_id} {{
            color: #8b949e;
            font-size: 0.65rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 3px;
        }}
        .fc-val-{card_id} {{
            color: {color};
            font-size: 1.3rem;
            font-weight: 700;
            font-family: 'SF Mono', 'Consolas', monospace;
        }}
        .fc-eq-{card_id} {{
            color: #58a6ff;
            font-size: 0.6rem;
            font-family: 'SF Mono', 'Consolas', monospace;
            margin-bottom: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .fc-ins-{card_id} {{
            color: #c9d1d9;
            font-size: 0.62rem;
            line-height: 1.25;
        }}
    </style>
    <div class="fc-{card_id}" onclick="this.classList.toggle('flipped')">
        <div class="fc-inner-{card_id}">
            <div class="fc-front-{card_id}">
                <div class="fc-lbl-{card_id}">{label}</div>
                <div class="fc-val-{card_id}">{formatted}</div>
            </div>
            <div class="fc-back-{card_id}">
                <div class="fc-eq-{card_id}">{equation}</div>
                <div class="fc-ins-{card_id}">{insight}</div>
                {bench_html}
            </div>
        </div>
    </div>
    """
    
    return html


def render_flip_cards_grid(metrics: List[Dict], components: Dict, columns: int = 5) -> None:
    """Render grid of flip cards."""
    
    if not metrics:
        return
    
    rows = (len(metrics) + columns - 1) // columns
    height = rows * 95 + 15
    
    grid_html = f"""
    <style>
        .flip-grid {{
            display: grid;
            grid-template-columns: repeat({columns}, 1fr);
            gap: 8px;
            padding: 4px;
        }}
        @media (max-width: 900px) {{
            .flip-grid {{ grid-template-columns: repeat(3, 1fr); }}
        }}
        @media (max-width: 600px) {{
            .flip-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
    </style>
    <div class="flip-grid">
    """
    
    for i, m in enumerate(metrics):
        card = create_flip_card(
            metric_key=m.get("key", f"m{i}"),
            value=m.get("value"),
            label=m.get("label", "Metric"),
            components=components,
            card_id=f"c{i}_{hashlib.md5(str(m).encode()).hexdigest()[:4]}"
        )
        grid_html += f"<div>{card}</div>"
    
    grid_html += "</div>"
    
    components_module = components  # Avoid name conflict
    st.components.v1.html(grid_html, height=height, scrolling=False)


def render_dashboard_flip_cards(financials: Dict) -> None:
    """Render dashboard with actual equation components."""
    
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
    
    # Extract all component values for equations
    price = get_val(['currentPrice', 'current_price', 'regularMarketPrice'])
    eps = get_val(['trailingEps', 'eps'])
    net_income = get_val(['netIncome', 'net_income'])
    revenue = get_val(['totalRevenue', 'revenue'])
    gross_profit = get_val(['grossProfit', 'gross_profit'])
    cogs = None
    if revenue and gross_profit:
        cogs = revenue - gross_profit
    total_debt = get_val(['totalDebt', 'total_debt'])
    equity = get_val(['totalStockholderEquity', 'stockholdersEquity', 'total_equity'])
    shares = get_val(['sharesOutstanding', 'shares_outstanding'])
    market_cap = get_val(['marketCap', 'market_cap'])
    fcf = get_val(['freeCashflow', 'free_cash_flow'])
    annual_div = get_val(['dividendRate', 'annual_dividend'])
    current_assets = get_val(['totalCurrentAssets', 'current_assets'])
    current_liab = get_val(['totalCurrentLiabilities', 'current_liabilities'])
    
    # Components dict for equation building
    comp = {
        "price": price,
        "eps": eps,
        "net_income": net_income,
        "revenue": revenue,
        "gross_profit": gross_profit,
        "cogs": cogs,
        "total_debt": total_debt,
        "equity": equity,
        "shares": shares,
        "market_cap": market_cap,
        "fcf": fcf,
        "annual_div": annual_div,
        "current_assets": current_assets,
        "current_liab": current_liab
    }
    
    # Calculate derived values
    pe_ratio = get_val(['trailingPE', 'PE_Ratio', 'pe_ratio'])
    roe = get_val(['ROE', 'roe', 'returnOnEquity'])
    de_ratio = get_val(['Debt_to_Equity', 'debt_to_equity', 'debtToEquity'])
    gross_margin = get_val(['Gross_Margin', 'gross_margin', 'grossMargins'])
    
    fcf_yield = None
    if fcf and market_cap and market_cap > 0:
        fcf_yield = (fcf / market_cap) * 100
    
    div_yield = get_val(['dividendYield'])
    if div_yield and div_yield < 1:
        div_yield = div_yield * 100
    
    beta = get_val(['beta'])
    
    metrics = [
        {"key": "PE_Ratio", "value": pe_ratio, "label": "P/E"},
        {"key": "current_price", "value": price, "label": "Price"},
        {"key": "ROE", "value": roe, "label": "ROE"},
        {"key": "Debt_to_Equity", "value": de_ratio, "label": "D/E"},
        {"key": "Gross_Margin", "value": gross_margin, "label": "Gross Margin"},
        {"key": "EPS", "value": eps, "label": "EPS"},
        {"key": "market_cap", "value": market_cap, "label": "Mkt Cap"},
        {"key": "FCF_Yield", "value": fcf_yield, "label": "FCF Yield"},
        {"key": "Beta", "value": beta, "label": "Beta"},
        {"key": "Dividend_Yield", "value": div_yield, "label": "Div Yield"},
    ]
    
    st.markdown("### Key Metrics")
    st.caption("Click any card to see equation & insight")
    
    render_flip_cards_grid(metrics, comp, columns=5)


# Exports
METRIC_INSIGHTS = METRIC_CONFIG  # Alias for compatibility
__all__ = ['render_dashboard_flip_cards', 'render_flip_cards_grid', 'METRIC_INSIGHTS', 'METRIC_CONFIG']
