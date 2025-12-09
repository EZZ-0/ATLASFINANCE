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
    from flip_cards import RATIO_DEFINITIONS, render_flip_card
    FLIP_CARDS_AVAILABLE = True
except ImportError:
    FLIP_CARDS_AVAILABLE = False
    RATIO_DEFINITIONS = {}
    def render_flip_card(*args, **kwargs): pass

# Import universal field mapper for intelligent field lookups
try:
    from utils.field_mapper import get_field
except ImportError:
    # Fallback if field_mapper not available
    def get_field(data, key, default=None):
        return data.get(key, default) if data else default


def render_earnings_flip_metrics(earnings_data: Dict, depth: str = "beginner"):
    """Render earnings metrics as flip cards"""
    if not FLIP_CARDS_AVAILABLE or not earnings_data or earnings_data.get('status') != 'success':
        return
    
    metrics = earnings_data.get('metrics', {})
    
    st.markdown("##### Key Earnings Metrics (Click to flip)")
    cols = st.columns(4)
    
    metric_list = [
        {"label": "Earnings Score", "value": metrics.get('earnings_score', metrics.get('beat_rate', 0) * 0.8 if metrics.get('beat_rate') else None), "format": "score", "benchmark": (60, 80)},
        {"label": "Beat Rate", "value": metrics.get('beat_rate'), "format": "pct", "benchmark": (50, 75)},
        {"label": "Avg Surprise", "value": metrics.get('average_surprise_pct', metrics.get('avg_surprise_pct')), "format": "pct"},
        {"label": "EPS Momentum", "value": metrics.get('quality_ratio', metrics.get('eps_momentum')), "format": "pct", "benchmark": (-10, 20)},
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
        {"label": "Dividend Yield", "value": metrics.get('yield_pct', metrics.get('dividend_yield')), "format": "pct", "benchmark": (2, 5)},
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
        {"label": "P/E Ratio", "value": metrics.get('pe_ratio', metrics.get('pe_trailing')), "format": "ratio", "benchmark": (15, 25), "higher_better": False},
        {"label": "PEG Ratio", "value": metrics.get('peg_ratio'), "format": "ratio", "benchmark": (1, 2), "higher_better": False},
        {"label": "P/B Ratio", "value": metrics.get('price_to_book'), "format": "ratio", "benchmark": (1, 3), "higher_better": False},
        {"label": "EV/EBITDA", "value": metrics.get('ev_to_ebitda'), "format": "ratio", "benchmark": (8, 15), "higher_better": False},
        {"label": "P/S Ratio", "value": metrics.get('price_to_sales', metrics.get('valuation_score')), "format": "ratio", "benchmark": (1, 5), "higher_better": False},
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
        {"label": "FCF Score", "value": metrics.get('cashflow_score', metrics.get('fcf_score')), "format": "score", "benchmark": (60, 80)},
        {"label": "FCF Yield", "value": metrics.get('fcf_yield', metrics.get('fcf_margin')), "format": "pct", "benchmark": (3, 8)},
        {"label": "OCF Margin", "value": metrics.get('ocf_margin'), "format": "pct", "benchmark": (15, 25)},
        {"label": "FCF Conversion", "value": metrics.get('fcf_conversion_rate', metrics.get('fcf_conversion')), "format": "pct", "benchmark": (80, 100)},
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
        {"label": "Health Score", "value": metrics.get('health_score', metrics.get('balance_sheet_score')), "format": "score", "benchmark": (60, 80)},
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
        {"label": "ROE", "value": metrics.get('roe', metrics.get('return_on_equity')), "format": "pct", "benchmark": (10, 20)},
        {"label": "ROA", "value": metrics.get('roa', metrics.get('return_on_assets')), "format": "pct", "benchmark": (5, 10)},
        {"label": "Asset Turnover", "value": metrics.get('roic', metrics.get('asset_turnover')), "format": "ratio", "benchmark": (0.5, 1.5)},
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
        {"label": "Growth Score", "value": metrics.get('growth_quality_score'), "format": "score", "benchmark": (60, 80)},
        {"label": "Revenue CAGR", "value": metrics.get('revenue_growth_rate'), "format": "pct", "benchmark": (5, 15)},
        {"label": "EPS CAGR", "value": metrics.get('earnings_growth_rate'), "format": "pct", "benchmark": (5, 20)},
        {"label": "Consistency", "value": metrics.get('revenue_growth_volatility'), "format": "pct", "benchmark": (60, 80), "higher_better": False},
    ]
    
    for i, m in enumerate(metric_list):
        with cols[i]:
            _render_analysis_flip(m, depth)


def _render_analysis_flip(config: Dict, depth: str):
    """Render a single analysis flip card using unified CSS flip cards"""
    
    label = config["label"]
    value = config["value"]
    
    # Map label to metric key for flip_cards.py
    key_mapping = {
        # Valuation
        "P/E Ratio": "PE_Ratio",
        "P/B Ratio": "PB_Ratio",
        "P/S Ratio": "P_S_Ratio",
        "EV/EBITDA": "EV_EBITDA",
        "PEG Ratio": "PEG_Ratio",
        # Profitability
        "ROE": "ROE",
        "ROA": "ROA",
        "ROIC": "ROIC",
        "Gross Margin": "Gross_Margin",
        "Operating Margin": "Operating_Margin",
        "Profit Margin": "Profit_Margin",
        # Balance Sheet
        "Current Ratio": "Current_Ratio",
        "Quick Ratio": "Quick_Ratio",
        "Debt/Equity": "Debt_to_Equity",
        "Interest Coverage": "Interest_Coverage",
        "Health Score": "Health_Score",
        # Dividends
        "Dividend Yield": "Dividend_Yield",
        "Payout Ratio": "Payout_Ratio",
        "5Y Growth": "5Y_Growth",
        "Streak Years": "Streak_Years",
        # Earnings
        "Earnings Score": "Earnings_Score",
        "Beat Rate": "Beat_Rate",
        "Avg Surprise": "Avg_Surprise",
        "EPS Momentum": "EPS_Momentum",
        # Cash Flow
        "FCF Yield": "FCF_Yield",
        "FCF Score": "FCF_Score",
        "OCF Margin": "OCF_Margin",
        "FCF Conversion": "FCF_Conversion",
        # Management
        "Mgmt Score": "Mgmt_Score",
        "Asset Turnover": "Asset_Turnover",
        # Growth
        "Growth Score": "Growth_Score",
        "Revenue CAGR": "Revenue_CAGR",
        "Revenue Growth": "Revenue_Growth",
        "EPS CAGR": "EPS_CAGR",
        "EPS Growth": "EPS_Growth",
        "Consistency": "Consistency",
    }
    
    metric_key = key_mapping.get(label, label.replace(" ", "_"))
    
    # Use the new unified CSS flip card (no st.rerun needed)
    render_flip_card(
        metric_key=metric_key,
        value=value,
        label=label,
        height=130
    )

