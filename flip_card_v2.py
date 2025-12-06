"""
FLIP CARD V2.1 - Professional Compact Design
=============================================
Pure HTML/CSS/JavaScript for smooth 60fps flip animation.

Design Principles:
- Compact cards (same size front/back)
- Brief actionable insights (not textbook)
- Color-coded by actual state (validated)
- Data validation to catch errors
- Professional sleek appearance

Target: CFOs, Analysts, Finance Students - unified experience
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, List
import pandas as pd
import hashlib

# ============================================================================
# METRIC DEFINITIONS - Brief Actionable Insights
# ============================================================================

METRIC_INSIGHTS = {
    "PE_Ratio": {
        "name": "P/E Ratio",
        "formula": "Price ÷ EPS",
        "insight": "Investor sentiment per $1 earnings. Compare to sector peers.",
        "benchmark": {"low": 15, "high": 25, "unit": "x"},
        "higher_is_better": False,
        "valid_range": (0, 500)  # Validation: P/E shouldn't be negative or >500
    },
    "PB_Ratio": {
        "name": "P/B Ratio",
        "formula": "Price ÷ Book Value",
        "insight": "Market vs accounting value. <1 may be undervalued.",
        "benchmark": {"low": 1, "high": 3, "unit": "x"},
        "higher_is_better": False,
        "valid_range": (0, 100)
    },
    "ROE": {
        "name": "ROE",
        "formula": "Net Income ÷ Equity",
        "insight": "Profit per shareholder dollar. >15% is strong.",
        "benchmark": {"low": 10, "high": 20, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (-100, 200)  # Can be negative
    },
    "ROA": {
        "name": "ROA",
        "formula": "Net Income ÷ Assets",
        "insight": "Asset efficiency. Varies by industry.",
        "benchmark": {"low": 5, "high": 10, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (-50, 100)
    },
    "Current_Ratio": {
        "name": "Current Ratio",
        "formula": "Current Assets ÷ Current Liab",
        "insight": "Short-term liquidity. >1.5 is comfortable.",
        "benchmark": {"low": 1.0, "high": 2.0, "unit": "x"},
        "higher_is_better": True,
        "valid_range": (0, 20)
    },
    "Debt_to_Equity": {
        "name": "D/E Ratio",
        "formula": "Total Debt ÷ Equity",
        "insight": "Leverage risk. <1 is conservative.",
        "benchmark": {"low": 0.5, "high": 1.5, "unit": "x"},
        "higher_is_better": False,
        "valid_range": (0, 50)  # Can't be negative, shouldn't be >50
    },
    "Gross_Margin": {
        "name": "Gross Margin",
        "formula": "(Revenue - COGS) ÷ Revenue",
        "insight": "Pricing power. >40% indicates strength.",
        "benchmark": {"low": 30, "high": 50, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (-50, 100)
    },
    "Operating_Margin": {
        "name": "Op. Margin",
        "formula": "Operating Income ÷ Revenue",
        "insight": "Operational efficiency after OpEx.",
        "benchmark": {"low": 10, "high": 20, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (-100, 100)
    },
    "Net_Margin": {
        "name": "Net Margin",
        "formula": "Net Income ÷ Revenue",
        "insight": "Bottom line per $1 revenue.",
        "benchmark": {"low": 5, "high": 15, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (-100, 100)
    },
    "EV_EBITDA": {
        "name": "EV/EBITDA",
        "formula": "Enterprise Value ÷ EBITDA",
        "insight": "Capital-neutral valuation. <10 may be cheap.",
        "benchmark": {"low": 8, "high": 15, "unit": "x"},
        "higher_is_better": False,
        "valid_range": (0, 100)
    },
    "FCF_Yield": {
        "name": "FCF Yield",
        "formula": "Free Cash Flow ÷ Market Cap",
        "insight": "Cash generation vs price. >5% is attractive.",
        "benchmark": {"low": 3, "high": 8, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (-50, 50)
    },
    "Dividend_Yield": {
        "name": "Div. Yield",
        "formula": "Annual Dividend ÷ Price",
        "insight": "Income return. >4% is high yield.",
        "benchmark": {"low": 2, "high": 5, "unit": "%"},
        "higher_is_better": True,
        "valid_range": (0, 20)  # Can't be >20% realistically
    },
    "Beta": {
        "name": "Beta",
        "formula": "Stock Volatility vs Market",
        "insight": "Risk measure. >1 = more volatile than market.",
        "benchmark": {"low": 0.8, "high": 1.2, "unit": ""},
        "higher_is_better": None,  # Neutral
        "valid_range": (-2, 5)
    },
    "EPS": {
        "name": "EPS",
        "formula": "Net Income ÷ Shares",
        "insight": "Earnings per share. Growth matters more.",
        "benchmark": {"low": 1, "high": 10, "unit": "$"},
        "higher_is_better": True,
        "valid_range": (-100, 1000)
    },
    "current_price": {
        "name": "Price",
        "formula": "Current Market Price",
        "insight": "Market price. Compare to intrinsic value.",
        "benchmark": None,
        "higher_is_better": None,
        "valid_range": (0.01, 100000)
    },
    "market_cap": {
        "name": "Market Cap",
        "formula": "Price × Shares Outstanding",
        "insight": "Company size. Large cap >$10B.",
        "benchmark": None,
        "higher_is_better": None,
        "valid_range": (1e6, 1e14)
    }
}


def validate_metric(value: Any, metric_key: str) -> tuple:
    """
    Validate metric value against expected range.
    
    Returns:
        (validated_value, is_valid, warning_msg)
    """
    if value is None:
        return None, False, "No data"
    
    try:
        num = float(value)
        if pd.isna(num):
            return None, False, "No data"
    except (ValueError, TypeError):
        return None, False, "Invalid"
    
    config = METRIC_INSIGHTS.get(metric_key, {})
    valid_range = config.get("valid_range")
    
    if valid_range:
        low, high = valid_range
        if num < low or num > high:
            return num, False, f"Suspicious ({num:.2f})"
    
    return num, True, None


def get_metric_color(value: float, metric_key: str, is_valid: bool) -> str:
    """
    Get color based on metric value and benchmarks.
    
    Returns color hex code.
    """
    if not is_valid or value is None:
        return "#6b7280"  # Gray for invalid/N/A
    
    config = METRIC_INSIGHTS.get(metric_key, {})
    benchmark = config.get("benchmark")
    higher_is_better = config.get("higher_is_better")
    
    if benchmark is None or higher_is_better is None:
        return "#60a5fa"  # Blue for neutral metrics
    
    low = benchmark.get("low", 0)
    high = benchmark.get("high", 100)
    
    if higher_is_better:
        if value >= high:
            return "#10b981"  # Green - excellent
        elif value <= low:
            return "#ef4444"  # Red - poor
        else:
            return "#f59e0b"  # Yellow - moderate
    else:  # Lower is better
        if value <= low:
            return "#10b981"  # Green - excellent
        elif value >= high:
            return "#ef4444"  # Red - poor
        else:
            return "#f59e0b"  # Yellow - moderate


def format_metric_value(value: float, unit: str, metric_key: str) -> str:
    """Format metric value with proper units and 2 decimal precision."""
    
    if value is None:
        return "N/A"
    
    try:
        num = float(value)
    except:
        return "N/A"
    
    # Handle percentage conversion for ratios stored as decimals
    if unit == "%" and metric_key in ["ROE", "ROA", "Gross_Margin", "Operating_Margin", "Net_Margin", "FCF_Yield", "Dividend_Yield"]:
        # If value looks like a decimal ratio (< 1), convert to percentage
        if abs(num) < 1:
            num = num * 100
    
    # Handle D/E ratio that might be stored as percentage
    if metric_key == "Debt_to_Equity" and num > 10:
        num = num / 100  # Convert from percentage to ratio
    
    # Format based on unit
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


def create_compact_flip_card(
    metric_key: str,
    value: Any,
    label: str,
    unit: str = "",
    card_id: str = None
) -> str:
    """
    Create a compact professional flip card.
    Same size front and back, brief insight, proper colors.
    """
    
    if card_id is None:
        card_id = hashlib.md5(f"{metric_key}_{label}".encode()).hexdigest()[:8]
    
    # Validate and get color
    validated_value, is_valid, warning = validate_metric(value, metric_key)
    color = get_metric_color(validated_value, metric_key, is_valid)
    
    # Get config
    config = METRIC_INSIGHTS.get(metric_key, {})
    metric_name = config.get("name", label)
    formula = config.get("formula", "")
    insight = config.get("insight", "")
    benchmark = config.get("benchmark", {})
    bench_unit = benchmark.get("unit", "") if benchmark else ""
    
    # Format value
    formatted_value = format_metric_value(validated_value, unit or bench_unit, metric_key)
    
    # Add warning indicator if invalid
    if not is_valid and warning:
        formatted_value = f"{formatted_value}*"
    
    # Benchmark range text
    bench_text = ""
    if benchmark:
        low = benchmark.get("low", "")
        high = benchmark.get("high", "")
        if low and high:
            bench_text = f"Range: {low}-{high}{bench_unit}"
    
    html = f"""
    <style>
        .fc-{card_id} {{
            perspective: 800px;
            width: 100%;
            height: 90px;
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
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
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
            padding: 10px 12px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.2);
            border-left: 3px solid {color};
            background: linear-gradient(145deg, #1a2332 0%, #0d1117 100%);
        }}
        .fc-back-{card_id} {{
            transform: rotateY(180deg);
        }}
        .fc-label-{card_id} {{
            color: #8b949e;
            font-size: 0.7rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 4px;
        }}
        .fc-value-{card_id} {{
            color: {color};
            font-size: 1.4rem;
            font-weight: 700;
            font-family: 'SF Mono', 'Consolas', monospace;
            line-height: 1.2;
        }}
        .fc-formula-{card_id} {{
            color: #58a6ff;
            font-size: 0.65rem;
            font-family: 'SF Mono', 'Consolas', monospace;
            margin-bottom: 4px;
        }}
        .fc-insight-{card_id} {{
            color: #c9d1d9;
            font-size: 0.68rem;
            line-height: 1.3;
        }}
        .fc-bench-{card_id} {{
            color: #6e7681;
            font-size: 0.6rem;
            margin-top: 3px;
        }}
    </style>
    <div class="fc-{card_id}" onclick="this.classList.toggle('flipped')">
        <div class="fc-inner-{card_id}">
            <div class="fc-front-{card_id}">
                <div class="fc-label-{card_id}">{label}</div>
                <div class="fc-value-{card_id}">{formatted_value}</div>
            </div>
            <div class="fc-back-{card_id}">
                <div class="fc-formula-{card_id}">{formula}</div>
                <div class="fc-insight-{card_id}">{insight}</div>
                <div class="fc-bench-{card_id}">{bench_text}</div>
            </div>
        </div>
    </div>
    """
    
    return html


def render_flip_cards_grid(metrics: List[Dict], columns: int = 5) -> None:
    """Render metrics as a compact grid of flip cards."""
    
    if not metrics:
        return
    
    rows = (len(metrics) + columns - 1) // columns
    height = rows * 100 + 20
    
    grid_html = f"""
    <style>
        .flip-grid {{
            display: grid;
            grid-template-columns: repeat({columns}, 1fr);
            gap: 10px;
            padding: 5px;
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
        card = create_compact_flip_card(
            metric_key=m.get("key", f"m{i}"),
            value=m.get("value"),
            label=m.get("label", "Metric"),
            unit=m.get("unit", ""),
            card_id=f"c{i}_{hashlib.md5(str(m).encode()).hexdigest()[:4]}"
        )
        grid_html += f"<div>{card}</div>"
    
    grid_html += "</div>"
    
    components.html(grid_html, height=height, scrolling=False)


def render_dashboard_flip_cards(financials: Dict) -> None:
    """Render dashboard metrics with proper data extraction and validation."""
    
    info = financials.get('info', {})
    market_data = financials.get('market_data', {})
    ratios = financials.get('ratios', pd.DataFrame())
    
    def get_val(keys, default=None):
        """Extract value from multiple possible sources."""
        sources = [info, market_data, financials]
        
        for src in sources:
            if not isinstance(src, dict):
                continue
            for k in (keys if isinstance(keys, list) else [keys]):
                if k in src and src[k] is not None:
                    v = src[k]
                    if not (isinstance(v, float) and pd.isna(v)):
                        return v
        
        # Try ratios DataFrame
        if isinstance(ratios, pd.DataFrame) and not ratios.empty:
            for k in (keys if isinstance(keys, list) else [keys]):
                if k in ratios.index:
                    v = ratios.loc[k].iloc[0]
                    if pd.notna(v):
                        return v
        
        return default
    
    # Get current price for FCF yield calculation
    price = get_val(['currentPrice', 'current_price', 'regularMarketPrice'])
    fcf = get_val(['freeCashflow', 'free_cash_flow'])
    market_cap = get_val(['marketCap', 'market_cap'])
    
    # Calculate FCF Yield properly
    fcf_yield = None
    if fcf and market_cap and market_cap > 0:
        fcf_yield = (fcf / market_cap) * 100
    
    # Get dividend yield (comes as decimal from yfinance)
    div_yield = get_val(['dividendYield'])
    if div_yield and div_yield < 1:
        div_yield = div_yield * 100  # Convert to percentage
    
    # Get D/E ratio - handle different formats
    de_ratio = get_val(['Debt_to_Equity', 'debt_to_equity', 'debtToEquity'])
    if de_ratio and de_ratio > 10:
        de_ratio = de_ratio / 100  # Convert if stored as percentage
    
    # Get ROE - handle decimal vs percentage
    roe = get_val(['ROE', 'roe', 'returnOnEquity'])
    if roe and abs(roe) < 1:
        roe = roe * 100  # Convert to percentage
    
    # Get Gross Margin
    gross_margin = get_val(['Gross_Margin', 'gross_margin', 'grossMargins'])
    if gross_margin and abs(gross_margin) < 1:
        gross_margin = gross_margin * 100
    
    metrics = [
        {"key": "PE_Ratio", "value": get_val(['trailingPE', 'PE_Ratio', 'pe_ratio']), "label": "P/E", "unit": "x"},
        {"key": "current_price", "value": price, "label": "Price", "unit": "$"},
        {"key": "ROE", "value": roe, "label": "ROE", "unit": "%"},
        {"key": "Debt_to_Equity", "value": de_ratio, "label": "D/E", "unit": "x"},
        {"key": "Gross_Margin", "value": gross_margin, "label": "Gross Margin", "unit": "%"},
        {"key": "EPS", "value": get_val(['trailingEps', 'eps']), "label": "EPS", "unit": "$"},
        {"key": "market_cap", "value": market_cap, "label": "Mkt Cap", "unit": "$"},
        {"key": "FCF_Yield", "value": fcf_yield, "label": "FCF Yield", "unit": "%"},
        {"key": "Beta", "value": get_val(['beta']), "label": "Beta", "unit": "x"},
        {"key": "Dividend_Yield", "value": div_yield, "label": "Div Yield", "unit": "%"},
    ]
    
    st.markdown("### Key Metrics")
    st.caption("Click any card for formula & insight")
    
    render_flip_cards_grid(metrics, columns=5)


# Export
__all__ = ['render_dashboard_flip_cards', 'render_flip_cards_grid', 'METRIC_INSIGHTS']
