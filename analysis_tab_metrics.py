"""
Analysis Tab Flip Card Metrics
==============================
Provides flip card metric displays for the Analysis tab sub-tabs.

Sub-tabs:
1. Earnings - Beat rate, surprise, quality score
2. Dividends - Yield, payout ratio, growth
3. Valuation - P/E, P/B, P/S, EV/EBITDA
4. Cash Flow - FCF, OCF, conversion
5. Balance Sheet - Current ratio, D/E, health score
6. Management - ROE, ROA, ROIC
7. Growth Quality - Revenue/EPS CAGR, consistency
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

# Import flip card components with fallback
try:
    from flip_card_component import RATIO_DEFINITIONS
    FLIP_CARDS_AVAILABLE = True
except ImportError:
    FLIP_CARDS_AVAILABLE = False
    RATIO_DEFINITIONS = {}


def render_earnings_flip_metrics(earnings_data: Dict, depth: str = "beginner"):
    """Render earnings metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not earnings_data or earnings_data.get('status') != 'success':
        return
    
    metrics = earnings_data.get('metrics', {})
    
    st.markdown("##### Key Earnings Metrics (Click to flip)")
    cols = st.columns(4)
    
    metric_list = [
        {"label": "Earnings Score", "value": metrics.get('earnings_score'), "format": "score", "benchmark": (60, 80)},
        {"label": "Beat Rate", "value": metrics.get('beat_rate'), "format": "pct", "benchmark": (50, 75)},
        {"label": "Avg Surprise", "value": metrics.get('average_surprise_pct'), "format": "pct"},
        {"label": "Quality Ratio", "value": metrics.get('quality_ratio'), "format": "ratio", "benchmark": (0.5, 1.0)},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def render_dividend_flip_metrics(dividend_data: Dict, depth: str = "beginner"):
    """Render dividend metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not dividend_data or dividend_data.get('status') != 'success':
        return
    
    metrics = dividend_data.get('metrics', {})
    
    st.markdown("##### Key Dividend Metrics (Click to flip)")
    cols = st.columns(4)
    
    metric_list = [
        {"label": "Dividend Yield", "value": metrics.get('yield_pct'), "format": "pct", "benchmark": (2, 5)},
        {"label": "Payout Ratio", "value": metrics.get('payout_ratio'), "format": "pct", "benchmark": (30, 60), "higher_better": False},
        {"label": "5Y Growth", "value": metrics.get('dividend_cagr_5y'), "format": "pct", "benchmark": (3, 10)},
        {"label": "Streak Years", "value": metrics.get('consecutive_years'), "format": "years", "benchmark": (5, 25)},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def render_valuation_flip_metrics(valuation_data: Dict, depth: str = "beginner"):
    """Render valuation metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not valuation_data or valuation_data.get('status') != 'success':
        return
    
    metrics = valuation_data.get('metrics', {})
    
    st.markdown("##### Key Valuation Metrics (Click to flip)")
    cols = st.columns(5)
    
    metric_list = [
        {"label": "P/E Ratio", "value": metrics.get('pe_ratio'), "format": "ratio", "benchmark": (15, 25), "higher_better": False},
        {"label": "PEG Ratio", "value": metrics.get('peg_ratio'), "format": "ratio", "benchmark": (1, 2), "higher_better": False},
        {"label": "P/B Ratio", "value": metrics.get('pb_ratio'), "format": "ratio", "benchmark": (1, 3), "higher_better": False},
        {"label": "EV/EBITDA", "value": metrics.get('ev_ebitda'), "format": "ratio", "benchmark": (8, 15), "higher_better": False},
        {"label": "Premium/Discount", "value": metrics.get('vs_sector_pct'), "format": "pct"},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def render_cashflow_flip_metrics(cashflow_data: Dict, depth: str = "beginner"):
    """Render cash flow metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not cashflow_data or cashflow_data.get('status') != 'success':
        return
    
    metrics = cashflow_data.get('metrics', {})
    
    st.markdown("##### Key Cash Flow Metrics (Click to flip)")
    cols = st.columns(4)
    
    metric_list = [
        {"label": "FCF Score", "value": metrics.get('fcf_score'), "format": "score", "benchmark": (60, 80)},
        {"label": "FCF Yield", "value": metrics.get('fcf_yield'), "format": "pct", "benchmark": (3, 8)},
        {"label": "OCF Margin", "value": metrics.get('ocf_margin'), "format": "pct", "benchmark": (15, 25)},
        {"label": "FCF Conversion", "value": metrics.get('fcf_conversion'), "format": "pct", "benchmark": (80, 100)},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def render_balance_flip_metrics(balance_data: Dict, depth: str = "beginner"):
    """Render balance sheet health metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not balance_data or balance_data.get('status') != 'success':
        return
    
    metrics = balance_data.get('metrics', {})
    
    st.markdown("##### Key Balance Sheet Metrics (Click to flip)")
    cols = st.columns(5)
    
    metric_list = [
        {"label": "Health Score", "value": metrics.get('health_score'), "format": "score", "benchmark": (60, 80)},
        {"label": "Current Ratio", "value": metrics.get('current_ratio'), "format": "ratio", "benchmark": (1.0, 2.0)},
        {"label": "Quick Ratio", "value": metrics.get('quick_ratio'), "format": "ratio", "benchmark": (0.8, 1.5)},
        {"label": "Debt/Equity", "value": metrics.get('debt_to_equity'), "format": "ratio", "benchmark": (0.5, 1.5), "higher_better": False},
        {"label": "Interest Coverage", "value": metrics.get('interest_coverage'), "format": "ratio", "benchmark": (3, 10)},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def render_management_flip_metrics(management_data: Dict, depth: str = "beginner"):
    """Render management effectiveness metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not management_data or management_data.get('status') != 'success':
        return
    
    metrics = management_data.get('metrics', {})
    
    st.markdown("##### Key Management Metrics (Click to flip)")
    cols = st.columns(4)
    
    metric_list = [
        {"label": "Mgmt Score", "value": metrics.get('management_score'), "format": "score", "benchmark": (60, 80)},
        {"label": "ROE", "value": metrics.get('roe'), "format": "pct", "benchmark": (10, 20)},
        {"label": "ROA", "value": metrics.get('roa'), "format": "pct", "benchmark": (5, 10)},
        {"label": "ROIC", "value": metrics.get('roic'), "format": "pct", "benchmark": (10, 20)},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def render_growth_flip_metrics(growth_data: Dict, depth: str = "beginner"):
    """Render growth quality metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not growth_data or growth_data.get('status') != 'success':
        return
    
    metrics = growth_data.get('metrics', {})
    
    st.markdown("##### Key Growth Metrics (Click to flip)")
    cols = st.columns(4)
    
    metric_list = [
        {"label": "Growth Score", "value": metrics.get('growth_score'), "format": "score", "benchmark": (60, 80)},
        {"label": "Revenue CAGR", "value": metrics.get('revenue_cagr_3y'), "format": "pct", "benchmark": (5, 15)},
        {"label": "EPS CAGR", "value": metrics.get('eps_cagr_3y'), "format": "pct", "benchmark": (5, 20)},
        {"label": "Consistency", "value": metrics.get('consistency_score'), "format": "score", "benchmark": (60, 80)},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def _render_analysis_flip(config: Dict, depth: str):
    """Render a single analysis flip card"""
    
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
            
            if fmt == "score":
                formatted = f"{num:.0f}/100"
            elif fmt == "pct":
                formatted = f"{num:.1f}%"
            elif fmt == "ratio":
                formatted = f"{num:.2f}x"
            elif fmt == "years":
                formatted = f"{int(num)} yrs"
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
                color = "#60a5fa"
                    
        except (ValueError, TypeError):
            formatted = str(value) if value else "N/A"
            color = "#6b7280"
    
    # Get explanation
    key_mapping = {
        "P/E Ratio": "PE_Ratio",
        "P/B Ratio": "PB_Ratio",
        "EV/EBITDA": "EV_EBITDA",
        "ROE": "ROE",
        "ROA": "ROA",
        "ROIC": "ROIC",
        "Current Ratio": "Current_Ratio",
        "Debt/Equity": "Debt_to_Equity",
        "Dividend Yield": "Dividend_Yield",
        "Payout Ratio": "Payout_Ratio",
        "PEG Ratio": "PEG_Ratio",
    }
    
    def_key = key_mapping.get(label, label.replace(" ", "_"))
    definition = RATIO_DEFINITIONS.get(def_key, {})
    formula = definition.get("formula", "")
    explanation = definition.get("explanations", {}).get(depth, f"Measures {label.lower()}")
    
    # Create unique key
    card_key = f"analysis_flip_{label.replace(' ', '_').replace('/', '_')}"
    
    if card_key not in st.session_state:
        st.session_state[card_key] = False
    
    is_flipped = st.session_state[card_key]
    
    # Render card (compact version for analysis tab)
    st.markdown(f"""
    <style>
        .analysis-flip-{card_key} {{
            perspective: 1000px;
            height: 100px;
            margin-bottom: 6px;
        }}
        .analysis-card-{card_key} {{
            position: relative;
            width: 100%;
            height: 100%;
            text-align: center;
            transition: transform 0.5s;
            transform-style: preserve-3d;
            cursor: pointer;
            border-radius: 8px;
        }}
        .analysis-card-{card_key}.flipped {{
            transform: rotateY(180deg);
        }}
        .analysis-front-{card_key}, .analysis-back-{card_key} {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }}
        .analysis-front-{card_key} {{
            background: linear-gradient(145deg, #1e293b, #0f172a);
            border-left: 3px solid {color};
        }}
        .analysis-back-{card_key} {{
            background: linear-gradient(145deg, #0f172a, #1e293b);
            border-left: 3px solid {color};
            transform: rotateY(180deg);
            text-align: left;
            font-size: 0.65rem;
            overflow-y: auto;
        }}
    </style>
    <div class="analysis-flip-{card_key}">
        <div class="analysis-card-{card_key} {'flipped' if is_flipped else ''}">
            <div class="analysis-front-{card_key}">
                <div style="color: #94a3b8; font-size: 0.7rem;">{label}</div>
                <div style="color: {color}; font-size: 1.3rem; font-weight: 700;">{formatted}</div>
            </div>
            <div class="analysis-back-{card_key}">
                <div style="font-weight: 600; color: #e2e8f0; font-size: 0.7rem;">{label}</div>
                <div style="color: #60a5fa; font-family: monospace; font-size: 0.6rem;">{formula[:50] if formula else ''}</div>
                <div style="color: #cbd5e1; font-size: 0.6rem; line-height: 1.2;">{explanation[:80]}{'...' if len(explanation) > 80 else ''}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle button
    if st.button("↻", key=f"btn_{card_key}", help="Flip"):
        st.session_state[card_key] = not st.session_state[card_key]
        st.rerun()

