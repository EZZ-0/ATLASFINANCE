"""
UNIFIED FLIP CARDS - MILESTONE-008 + MILESTONE-012
===================================================

Single source of truth for all flip card metrics across the app.
Click any metric to see formula breakdown + insight.

Features:
- Consistent sizing (same as st.metric)
- Smooth CSS animation (no server round-trip)
- Color-coded by performance
- Works in all tabs
- Bank-specific metric handling (M012)

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (MILESTONE-008)
Updated: 2025-12-08 (MILESTONE-012 - Bank handling)
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, Optional, List, Tuple, Union
import pandas as pd
import hashlib

# Import bank utilities
try:
    from utils.bank_metrics import is_bank, get_bank_display_metrics, BANK_TICKERS
    BANK_SUPPORT = True
except ImportError:
    BANK_SUPPORT = False
    BANK_TICKERS = set()

# Re-export RATIO_DEFINITIONS for backward compatibility with flip_card_component imports
try:
    from ratio_card import RATIO_DEFINITIONS
except ImportError:
    RATIO_DEFINITIONS = {}


# ============================================================================
# METRIC DEFINITIONS - All metrics with formulas, insights, benchmarks
# ============================================================================

METRICS = {
    # === VALUATION ===
    "PE_Ratio": {
        "label": "P/E Ratio",
        "formula": "Price ÷ EPS",
        "insight": "Investor sentiment per $1 earnings. Lower = cheaper.",
        "benchmark": (15, 25),
        "higher_is": "neutral",  # depends on context
        "unit": "x",
        "category": "Valuation"
    },
    "PB_Ratio": {
        "label": "P/B Ratio",
        "formula": "Price ÷ Book Value",
        "insight": "Premium over asset value. <1 may be undervalued.",
        "benchmark": (1, 3),
        "higher_is": "neutral",
        "unit": "x",
        "category": "Valuation"
    },
    "PS_Ratio": {
        "label": "P/S Ratio",
        "formula": "Price ÷ Revenue per Share",
        "insight": "What you pay per $1 of sales. Lower = cheaper.",
        "benchmark": (1, 5),
        "higher_is": "worse",
        "unit": "x",
        "category": "Valuation"
    },
    "EV_EBITDA": {
        "label": "EV/EBITDA",
        "formula": "Enterprise Value ÷ EBITDA",
        "insight": "Total company value vs cash earnings. <10 is attractive.",
        "benchmark": (8, 15),
        "higher_is": "worse",
        "unit": "x",
        "category": "Valuation"
    },
    "FCF_Yield": {
        "label": "FCF Yield",
        "formula": "Free Cash Flow ÷ Market Cap",
        "insight": "Cash generation vs price. >5% is attractive.",
        "benchmark": (3, 8),
        "higher_is": "better",
        "unit": "%",
        "category": "Valuation"
    },
    
    # === PROFITABILITY ===
    "ROE": {
        "label": "ROE",
        "formula": "Net Income ÷ Equity",
        "insight": "Profit per shareholder $. >15% is strong.",
        "benchmark": (10, 20),
        "higher_is": "better",
        "unit": "%",
        "category": "Profitability"
    },
    "ROA": {
        "label": "ROA",
        "formula": "Net Income ÷ Total Assets",
        "insight": "Asset efficiency. >5% is good.",
        "benchmark": (3, 10),
        "higher_is": "better",
        "unit": "%",
        "category": "Profitability"
    },
    "ROIC": {
        "label": "ROIC",
        "formula": "NOPAT ÷ Invested Capital",
        "insight": "Return on all capital. Should exceed WACC.",
        "benchmark": (8, 15),
        "higher_is": "better",
        "unit": "%",
        "category": "Profitability"
    },
    "Gross_Margin": {
        "label": "Gross Margin",
        "formula": "(Revenue - COGS) ÷ Revenue",
        "insight": "Pricing power. >40% is strong moat indicator.",
        "benchmark": (30, 50),
        "higher_is": "better",
        "unit": "%",
        "category": "Profitability"
    },
    "Operating_Margin": {
        "label": "Operating Margin",
        "formula": "Operating Income ÷ Revenue",
        "insight": "Core business efficiency. >15% is strong.",
        "benchmark": (10, 20),
        "higher_is": "better",
        "unit": "%",
        "category": "Profitability"
    },
    "Net_Margin": {
        "label": "Net Margin",
        "formula": "Net Income ÷ Revenue",
        "insight": "Bottom line efficiency. >10% is healthy.",
        "benchmark": (5, 15),
        "higher_is": "better",
        "unit": "%",
        "category": "Profitability"
    },
    
    # === LEVERAGE & SOLVENCY ===
    "Debt_to_Equity": {
        "label": "D/E Ratio",
        "formula": "Total Debt ÷ Equity",
        "insight": "Leverage risk. <1 is conservative, >2 is risky.",
        "benchmark": (0.5, 1.5),
        "higher_is": "worse",
        "unit": "x",
        "category": "Leverage"
    },
    "Current_Ratio": {
        "label": "Current Ratio",
        "formula": "Current Assets ÷ Current Liabilities",
        "insight": "Short-term liquidity. >1.5 is healthy.",
        "benchmark": (1.0, 2.0),
        "higher_is": "better",
        "unit": "x",
        "category": "Liquidity"
    },
    "Quick_Ratio": {
        "label": "Quick Ratio",
        "formula": "(Current Assets - Inventory) ÷ Current Liabilities",
        "insight": "Liquid assets coverage. >1 is safe.",
        "benchmark": (0.8, 1.5),
        "higher_is": "better",
        "unit": "x",
        "category": "Liquidity"
    },
    "Interest_Coverage": {
        "label": "Interest Coverage",
        "formula": "EBIT ÷ Interest Expense",
        "insight": "Ability to pay debt. >3 is safe, <1.5 is concerning.",
        "benchmark": (3, 8),
        "higher_is": "better",
        "unit": "x",
        "category": "Leverage"
    },
    
    # === GROWTH ===
    "Revenue_Growth": {
        "label": "Revenue Growth",
        "formula": "(Revenue - Prior Revenue) ÷ Prior Revenue",
        "insight": "Top-line growth rate. >10% for growth stocks.",
        "benchmark": (5, 20),
        "higher_is": "better",
        "unit": "%",
        "category": "Growth"
    },
    "EPS_Growth": {
        "label": "EPS Growth",
        "formula": "(EPS - Prior EPS) ÷ Prior EPS",
        "insight": "Earnings growth rate. Quality if faster than revenue.",
        "benchmark": (5, 25),
        "higher_is": "better",
        "unit": "%",
        "category": "Growth"
    },
    
    # === DIVIDENDS ===
    "Dividend_Yield": {
        "label": "Dividend Yield",
        "formula": "Annual Dividend ÷ Price",
        "insight": "Income return. >4% is high yield.",
        "benchmark": (2, 5),
        "higher_is": "better",
        "unit": "%",
        "category": "Dividends"
    },
    "Payout_Ratio": {
        "label": "Payout Ratio",
        "formula": "Dividends ÷ Net Income",
        "insight": "Sustainability. <60% is healthy, >80% risky.",
        "benchmark": (30, 60),
        "higher_is": "neutral",
        "unit": "%",
        "category": "Dividends"
    },
    
    # === MARKET DATA ===
    "current_price": {
        "label": "Price",
        "formula": "Market Price",
        "insight": "Compare to DCF intrinsic value.",
        "benchmark": None,
        "higher_is": "neutral",
        "unit": "$",
        "category": "Market"
    },
    "market_cap": {
        "label": "Market Cap",
        "formula": "Price × Shares Outstanding",
        "insight": "Company size. >$10B = large cap.",
        "benchmark": None,
        "higher_is": "neutral",
        "unit": "$",
        "category": "Market"
    },
    "EPS": {
        "label": "EPS",
        "formula": "Net Income ÷ Shares",
        "insight": "Earnings per share. Compare to price via P/E.",
        "benchmark": None,
        "higher_is": "better",
        "unit": "$",
        "category": "Earnings"
    },
    "Beta": {
        "label": "Beta",
        "formula": "Cov(Stock,Market) ÷ Var(Market)",
        "insight": "Volatility vs market. >1 = more volatile.",
        "benchmark": (0.8, 1.2),
        "higher_is": "neutral",
        "unit": "",
        "category": "Risk"
    },
    
    # === ALPHA SIGNALS ===
    "Earnings_Momentum": {
        "label": "Earnings Momentum",
        "formula": "Weighted revision changes",
        "insight": "Analyst estimate direction. Positive = bullish.",
        "benchmark": (-20, 20),
        "higher_is": "better",
        "unit": "",
        "category": "Alpha"
    },
    "Insider_Sentiment": {
        "label": "Insider Sentiment",
        "formula": "(Buys - Sells) weighted",
        "insight": "Insider activity signal. Positive = insiders buying.",
        "benchmark": (-30, 30),
        "higher_is": "better",
        "unit": "",
        "category": "Alpha"
    },
    "Institutional_Flow": {
        "label": "Inst. Accumulation",
        "formula": "Weighted holder changes",
        "insight": "Smart money flow. Positive = accumulating.",
        "benchmark": (-20, 20),
        "higher_is": "better",
        "unit": "",
        "category": "Alpha"
    },
}


# ============================================================================
# COLOR LOGIC
# ============================================================================

def get_metric_color(value: float, metric_key: str) -> str:
    """Get color based on value vs benchmark."""
    if value is None:
        return "#6b7280"  # Gray for N/A
    
    config = METRICS.get(metric_key, {})
    benchmark = config.get("benchmark")
    direction = config.get("higher_is", "neutral")
    
    if benchmark is None:
        return "#60a5fa"  # Blue for no benchmark
    
    low, high = benchmark
    
    if direction == "better":
        if value >= high:
            return "#10b981"  # Green
        elif value <= low:
            return "#ef4444"  # Red
        else:
            return "#f59e0b"  # Yellow
    elif direction == "worse":
        if value <= low:
            return "#10b981"  # Green
        elif value >= high:
            return "#ef4444"  # Red
        else:
            return "#f59e0b"  # Yellow
    else:
        # Neutral - use blue for in range, yellow for outside
        if low <= value <= high:
            return "#60a5fa"  # Blue
        else:
            return "#f59e0b"  # Yellow


# ============================================================================
# FORMATTING
# ============================================================================

def format_value(value: Any, unit: str) -> Tuple[str, Optional[float]]:
    """Format value for display. Returns (formatted_string, numeric_value)."""
    if value is None:
        return "N/A", None
    
    try:
        num = float(value)
        if pd.isna(num):
            return "N/A", None
    except (TypeError, ValueError):
        return str(value), None
    
    if unit == "$":
        if abs(num) >= 1e12:
            return f"${num/1e12:.2f}T", num
        elif abs(num) >= 1e9:
            return f"${num/1e9:.2f}B", num
        elif abs(num) >= 1e6:
            return f"${num/1e6:.1f}M", num
        else:
            return f"${num:.2f}", num
    elif unit == "%":
        # Auto-convert if looks like decimal
        display = num * 100 if abs(num) < 1 else num
        return f"{display:.1f}%", display
    elif unit == "x":
        return f"{num:.2f}x", num
    else:
        return f"{num:.2f}", num


# ============================================================================
# FLIP CARD RENDERER
# ============================================================================

def render_flip_card(
    metric_key: str,
    value: Any,
    label: str = None,
    custom_insight: str = None,
    height: int = 100
) -> None:
    """
    Render a single flip card in the current Streamlit column.
    
    Args:
        metric_key: Key from METRICS dict (e.g., "PE_Ratio")
        value: The metric value
        label: Override display label
        custom_insight: Override insight text
        height: Card height in pixels
    """
    config = METRICS.get(metric_key, {})
    
    display_label = label or config.get("label", metric_key)
    unit = config.get("unit", "")
    formula = config.get("formula", "")
    insight = custom_insight or config.get("insight", "")
    benchmark = config.get("benchmark")
    
    formatted, num_val = format_value(value, unit)
    color = get_metric_color(num_val, metric_key)
    
    # Handle N/A
    if formatted == "N/A":
        formula = ""
        insight = "Data not available"
        color = "#6b7280"
    
    bench_text = f"Benchmark: {benchmark[0]}-{benchmark[1]}{unit}" if benchmark else ""
    
    html = f"""
    <style>
        .fc-wrap {{
            perspective: 1000px;
            width: 100%;
            height: {height}px;
            cursor: pointer;
        }}
        .fc-inner {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.5s ease;
            transform-style: preserve-3d;
        }}
        .fc-wrap.flipped .fc-inner {{
            transform: rotateY(180deg);
        }}
        .fc-front, .fc-back {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 12px;
            background: linear-gradient(180deg, #1e2530 0%, #161b22 100%);
            border: 1px solid rgba(255,255,255,0.05);
        }}
        .fc-back {{
            transform: rotateY(180deg);
        }}
        .fc-label {{
            color: #8b949e;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }}
        .fc-value {{
            color: {color};
            font-size: 1.4rem;
            font-weight: 700;
        }}
        .fc-formula {{
            color: #58a6ff;
            font-size: 0.7rem;
            font-family: 'SF Mono', monospace;
            margin-bottom: 4px;
        }}
        .fc-insight {{
            color: #e6edf3;
            font-size: 0.7rem;
            line-height: 1.3;
        }}
        .fc-bench {{
            color: #6e7681;
            font-size: 0.6rem;
            margin-top: 4px;
        }}
    </style>
    <div class="fc-wrap" onclick="this.classList.toggle('flipped')">
        <div class="fc-inner">
            <div class="fc-front">
                <div class="fc-label">{display_label}</div>
                <div class="fc-value">{formatted}</div>
            </div>
            <div class="fc-back">
                <div class="fc-formula">{formula}</div>
                <div class="fc-insight">{insight}</div>
                <div class="fc-bench">{bench_text}</div>
            </div>
        </div>
    </div>
    """
    
    components.html(html, height=height + 10)


def render_flip_card_row(
    metrics: List[Dict],
    financials: Dict = None
) -> None:
    """
    Render a row of flip cards.
    
    Args:
        metrics: List of dicts with keys: 'key', 'value', 'label' (optional)
        financials: Optional financials dict to auto-extract values
    """
    if not metrics:
        return
    
    cols = st.columns(len(metrics))
    
    for i, m in enumerate(metrics):
        with cols[i]:
            render_flip_card(
                metric_key=m.get('key'),
                value=m.get('value'),
                label=m.get('label'),
                custom_insight=m.get('insight')
            )


# ============================================================================
# DASHBOARD INTEGRATION
# ============================================================================

def render_dashboard_metrics(financials: Dict, ticker: str = None) -> None:
    """
    Render key dashboard metrics as flip cards.
    
    M012: Bank-specific handling - shows P/B instead of D/E/FCF for banks.
    """
    
    info = financials.get('info', {})
    ratios = financials.get('ratios', pd.DataFrame())
    
    # Check if this is a bank (M012)
    ticker_str = ticker or info.get('symbol', '')
    is_bank_stock = BANK_SUPPORT and is_bank(ticker_str, info)
    
    def get_val(keys):
        """Get value from multiple sources."""
        if isinstance(keys, str):
            keys = [keys]
        
        # Try info dict
        for k in keys:
            if k in info and info[k] is not None:
                return info[k]
        
        # Try ratios DataFrame
        if isinstance(ratios, pd.DataFrame) and not ratios.empty:
            for k in keys:
                if k in ratios.index:
                    v = ratios.loc[k].iloc[0]
                    if pd.notna(v):
                        return v
        
        return None
    
    # Extract values
    pe = get_val(['trailingPE', 'PE_Ratio'])
    price = get_val(['currentPrice', 'regularMarketPrice'])
    roe = get_val(['returnOnEquity', 'ROE'])
    de = get_val(['debtToEquity', 'Debt_to_Equity'])
    gm = get_val(['grossMargins', 'Gross_Margin'])
    eps = get_val(['trailingEps', 'EPS'])
    mcap = get_val(['marketCap'])
    beta = get_val(['beta'])
    div_yield = get_val(['dividendYield'])
    fcf = get_val(['freeCashflow'])
    pb = get_val(['priceToBook'])
    
    # Calculate FCF Yield
    fcf_yield = (fcf / mcap * 100) if fcf and mcap and mcap > 0 else None
    
    st.markdown("### Key Metrics")
    if is_bank_stock:
        st.caption("Click any metric for insight (Bank-specific metrics shown)")
    else:
        st.caption("Click any metric to see formula & insight")
    
    # Row 1 - same for all
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_flip_card("PE_Ratio", pe)
    with c2:
        render_flip_card("current_price", price)
    with c3:
        render_flip_card("ROE", roe)
    with c4:
        # M012: Banks show P/B instead of D/E (D/E meaningless for banks)
        if is_bank_stock:
            render_flip_card("PB_Ratio", pb, "Price/Book", 
                           "Key bank valuation. <1 undervalued, >2 premium.")
        else:
            render_flip_card("Debt_to_Equity", de)
    with c5:
        render_flip_card("Gross_Margin", gm)
    
    # Row 2
    c6, c7, c8, c9, c10 = st.columns(5)
    with c6:
        render_flip_card("EPS", eps)
    with c7:
        render_flip_card("market_cap", mcap)
    with c8:
        # M012: Banks show Dividend Yield instead of FCF (FCF meaningless for banks)
        if is_bank_stock:
            render_flip_card("Dividend_Yield", div_yield, "Dividend Yield",
                           "Bank income return. Major banks pay 2-4%.")
        else:
            render_flip_card("FCF_Yield", fcf_yield)
    with c9:
        render_flip_card("Beta", beta)
    with c10:
        if is_bank_stock:
            # Show P/B again or another relevant metric
            render_flip_card("PB_Ratio", pb, "P/TBV Est.",
                           "Price to Tangible Book (approx).")
        else:
            render_flip_card("Dividend_Yield", div_yield)


# ============================================================================
# VALUATION METRICS
# ============================================================================

def render_valuation_metrics(financials: Dict) -> None:
    """Render valuation-focused flip cards."""
    
    info = financials.get('info', {})
    
    pe = info.get('trailingPE')
    pb = info.get('priceToBook')
    ps = info.get('priceToSalesTrailing12Months')
    ev_ebitda = info.get('enterpriseToEbitda')
    
    fcf = info.get('freeCashflow')
    mcap = info.get('marketCap')
    fcf_yield = (fcf / mcap * 100) if fcf and mcap and mcap > 0 else None
    
    st.markdown("#### Valuation Multiples")
    st.caption("Click to see formula & interpretation")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_flip_card("PE_Ratio", pe)
    with c2:
        render_flip_card("PB_Ratio", pb)
    with c3:
        render_flip_card("PS_Ratio", ps)
    with c4:
        render_flip_card("EV_EBITDA", ev_ebitda)
    with c5:
        render_flip_card("FCF_Yield", fcf_yield)


# ============================================================================
# ALPHA SIGNAL METRICS
# ============================================================================

def render_alpha_metrics(
    earnings_momentum: float = None,
    insider_sentiment: float = None,
    institutional_flow: float = None
) -> None:
    """Render alpha signal flip cards."""
    
    st.markdown("#### Alpha Signals")
    st.caption("Key predictive indicators")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        render_flip_card("Earnings_Momentum", earnings_momentum)
    with c2:
        render_flip_card("Insider_Sentiment", insider_sentiment)
    with c3:
        render_flip_card("Institutional_Flow", institutional_flow)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'METRICS',
    'render_flip_card',
    'render_flip_card_row',
    'render_dashboard_metrics',
    'render_valuation_metrics',
    'render_alpha_metrics',
    'get_metric_color',
    'format_value'
]

