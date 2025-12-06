"""
FLIP CARD V2 - Quizlet-Style Smooth Flip Cards
===============================================
Pure HTML/CSS/JavaScript implementation for smooth 60fps animations.
No Python callbacks - entirely client-side interaction.

Target Audience: CFOs, Senior Finance Students, Financial Analysts
Explanation Level: Professional (CFA/Intermediate balanced)

Features:
- CSS 3D transforms for hardware-accelerated animation
- Click anywhere on card to flip (no button)
- Touch-friendly for mobile
- 600ms smooth transition
- Professional dark theme
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Dict, Any, Optional, List
import pandas as pd
import json
import hashlib

# ============================================================================
# RATIO DEFINITIONS - Professional Level Only
# ============================================================================

PROFESSIONAL_DEFINITIONS = {
    "PE_Ratio": {
        "name": "Price-to-Earnings Ratio",
        "formula": "Market Price per Share ÷ Earnings per Share",
        "explanation": "Measures how much investors pay for each dollar of earnings. A P/E of 20x means investors pay $20 for every $1 of annual earnings. Compare to sector median and historical averages. High P/E may indicate growth expectations or overvaluation; low P/E may signal value opportunity or declining fundamentals.",
        "components": ["current_price", "eps"],
        "benchmark": {"low": 15, "high": 25},
        "higher_is_better": False
    },
    "PB_Ratio": {
        "name": "Price-to-Book Ratio",
        "formula": "Market Price per Share ÷ Book Value per Share",
        "explanation": "Compares market valuation to accounting net asset value. P/B < 1 suggests stock trades below liquidation value (potential value trap or opportunity). P/B > 3 typical for asset-light tech companies. Most useful for capital-intensive industries like banking and manufacturing.",
        "components": ["current_price", "book_value"],
        "benchmark": {"low": 1.0, "high": 3.0},
        "higher_is_better": False
    },
    "ROE": {
        "name": "Return on Equity",
        "formula": "Net Income ÷ Shareholders' Equity × 100",
        "explanation": "Measures profit generated per dollar of shareholder investment. ROE > 15% generally indicates efficient capital utilization. Decompose using DuPont analysis (Margin × Turnover × Leverage) to identify performance drivers. Beware high ROE from excessive leverage.",
        "components": ["net_income", "shareholders_equity"],
        "benchmark": {"low": 10, "high": 20},
        "higher_is_better": True
    },
    "ROA": {
        "name": "Return on Assets",
        "formula": "Net Income ÷ Total Assets × 100",
        "explanation": "Measures how efficiently management uses assets to generate profits. ROA > 5% is generally good; varies significantly by industry. Asset-heavy industries (utilities, manufacturing) typically have lower ROA than asset-light businesses (software, consulting).",
        "components": ["net_income", "total_assets"],
        "benchmark": {"low": 5, "high": 10},
        "higher_is_better": True
    },
    "Current_Ratio": {
        "name": "Current Ratio",
        "formula": "Current Assets ÷ Current Liabilities",
        "explanation": "Measures short-term liquidity and ability to meet obligations within 12 months. Ratio > 1.5 indicates comfortable liquidity buffer. Too high (> 3) may suggest inefficient asset utilization or excess inventory. Industry context matters: retailers often operate below 1.0.",
        "components": ["current_assets", "current_liabilities"],
        "benchmark": {"low": 1.0, "high": 2.0},
        "higher_is_better": True
    },
    "Quick_Ratio": {
        "name": "Quick Ratio (Acid Test)",
        "formula": "(Current Assets - Inventory) ÷ Current Liabilities",
        "explanation": "Stricter liquidity measure excluding inventory (harder to liquidate quickly). Ratio > 1.0 indicates ability to meet short-term obligations without selling inventory. Critical for businesses with slow-moving or perishable inventory.",
        "components": ["current_assets", "inventory", "current_liabilities"],
        "benchmark": {"low": 0.8, "high": 1.5},
        "higher_is_better": True
    },
    "Debt_to_Equity": {
        "name": "Debt-to-Equity Ratio",
        "formula": "Total Debt ÷ Shareholders' Equity",
        "explanation": "Measures financial leverage and capital structure risk. D/E > 2.0 indicates significant leverage; evaluate in context of interest coverage and debt maturity. Capital-intensive industries (utilities, airlines) typically carry higher leverage than technology companies.",
        "components": ["total_debt", "shareholders_equity"],
        "benchmark": {"low": 0.5, "high": 1.5},
        "higher_is_better": False
    },
    "Gross_Margin": {
        "name": "Gross Profit Margin",
        "formula": "(Revenue - COGS) ÷ Revenue × 100",
        "explanation": "Measures production efficiency and pricing power. Margin > 40% indicates strong pricing power or efficient operations. Trend analysis reveals competitive dynamics: declining margins may signal pricing pressure or rising input costs.",
        "components": ["revenue", "cogs", "gross_profit"],
        "benchmark": {"low": 30, "high": 50},
        "higher_is_better": True
    },
    "Operating_Margin": {
        "name": "Operating Profit Margin",
        "formula": "Operating Income ÷ Revenue × 100",
        "explanation": "Measures operational efficiency after all operating expenses. Margin > 15% indicates strong operating leverage. Excludes interest and taxes, making it useful for comparing companies with different capital structures.",
        "components": ["operating_income", "revenue"],
        "benchmark": {"low": 10, "high": 20},
        "higher_is_better": True
    },
    "Net_Margin": {
        "name": "Net Profit Margin",
        "formula": "Net Income ÷ Revenue × 100",
        "explanation": "Bottom-line profitability after all expenses, interest, and taxes. Margin > 10% is generally strong; varies significantly by industry. Trending margins reveal operational efficiency and pricing power dynamics over time.",
        "components": ["net_income", "revenue"],
        "benchmark": {"low": 5, "high": 15},
        "higher_is_better": True
    },
    "EV_EBITDA": {
        "name": "EV/EBITDA",
        "formula": "Enterprise Value ÷ EBITDA",
        "explanation": "Capital structure-neutral valuation metric. EV/EBITDA < 10x often considered undervalued; > 15x may indicate premium valuation. Preferred over P/E for comparing companies with different leverage. Does not account for CapEx requirements.",
        "components": ["enterprise_value", "ebitda"],
        "benchmark": {"low": 8, "high": 15},
        "higher_is_better": False
    },
    "FCF_Yield": {
        "name": "Free Cash Flow Yield",
        "formula": "Free Cash Flow ÷ Market Cap × 100",
        "explanation": "Measures cash generation relative to market value. Yield > 5% may indicate undervaluation or strong cash generation. Superior to dividend yield as it shows total cash available for dividends, buybacks, debt reduction, or reinvestment.",
        "components": ["free_cash_flow", "market_cap"],
        "benchmark": {"low": 3, "high": 8},
        "higher_is_better": True
    },
    "Dividend_Yield": {
        "name": "Dividend Yield",
        "formula": "Annual Dividend per Share ÷ Share Price × 100",
        "explanation": "Annual dividend income relative to stock price. Yield > 3% considered income-oriented; > 6% may signal dividend risk. Evaluate alongside payout ratio and FCF coverage to assess sustainability.",
        "components": ["annual_dividend", "current_price"],
        "benchmark": {"low": 2, "high": 5},
        "higher_is_better": True
    },
    "Payout_Ratio": {
        "name": "Dividend Payout Ratio",
        "formula": "Dividends per Share ÷ Earnings per Share × 100",
        "explanation": "Percentage of earnings distributed as dividends. Ratio < 60% typically sustainable; > 80% may indicate dividend stress. Mature companies tend higher ratios; growth companies reinvest more earnings.",
        "components": ["dividends", "eps"],
        "benchmark": {"low": 30, "high": 60},
        "higher_is_better": False
    },
    "Beta": {
        "name": "Beta (Market Sensitivity)",
        "formula": "Covariance(Stock, Market) ÷ Variance(Market)",
        "explanation": "Measures systematic risk relative to market. Beta = 1.0 moves with market; > 1.0 more volatile (higher risk/reward); < 1.0 defensive. Used in CAPM for cost of equity calculation. Historical beta may not predict future volatility.",
        "components": ["stock_returns", "market_returns"],
        "benchmark": {"low": 0.8, "high": 1.2},
        "higher_is_better": None  # Depends on strategy
    },
    "Interest_Coverage": {
        "name": "Interest Coverage Ratio",
        "formula": "EBIT ÷ Interest Expense",
        "explanation": "Measures ability to service debt obligations. Ratio > 3x indicates comfortable coverage; < 1.5x signals potential distress. Critical for credit analysis and debt capacity assessment.",
        "components": ["ebit", "interest_expense"],
        "benchmark": {"low": 3, "high": 10},
        "higher_is_better": True
    },
    "ROIC": {
        "name": "Return on Invested Capital",
        "formula": "NOPAT ÷ Invested Capital × 100",
        "explanation": "Measures return generated on all capital invested in the business. ROIC > WACC creates shareholder value; spread indicates competitive advantage. Preferred by value investors for assessing management capital allocation.",
        "components": ["nopat", "invested_capital"],
        "benchmark": {"low": 10, "high": 20},
        "higher_is_better": True
    },
    "Asset_Turnover": {
        "name": "Asset Turnover Ratio",
        "formula": "Revenue ÷ Average Total Assets",
        "explanation": "Measures revenue generated per dollar of assets. Higher turnover indicates efficient asset utilization. Part of DuPont analysis. Asset-light businesses (software) have high turnover; capital-intensive (manufacturing) have lower.",
        "components": ["revenue", "total_assets"],
        "benchmark": {"low": 0.5, "high": 1.5},
        "higher_is_better": True
    },
    "Altman_Z": {
        "name": "Altman Z-Score",
        "formula": "1.2×WC/TA + 1.4×RE/TA + 3.3×EBIT/TA + 0.6×ME/TL + 1.0×S/TA",
        "explanation": "Bankruptcy prediction model. Z > 2.99 indicates safety; 1.81-2.99 is gray zone; < 1.81 signals distress. Developed for manufacturing companies; variants exist for private and non-manufacturing firms.",
        "components": ["working_capital", "retained_earnings", "ebit", "market_cap", "total_liabilities", "revenue", "total_assets"],
        "benchmark": {"low": 1.81, "high": 2.99},
        "higher_is_better": True
    },
    "Beneish_M": {
        "name": "Beneish M-Score",
        "formula": "8-variable model detecting earnings manipulation",
        "explanation": "Forensic accounting metric identifying potential earnings manipulation. M-Score > -2.22 suggests higher probability of manipulation. Examines unusual changes in receivables, margins, asset quality, and accruals.",
        "components": ["receivables", "revenue", "gross_margin", "asset_quality", "depreciation", "sgna", "leverage", "accruals"],
        "benchmark": {"low": -2.5, "high": -2.22},
        "higher_is_better": False
    }
}


def create_flip_card_html(
    metric_key: str,
    value: Any,
    label: str,
    unit: str = "",
    card_id: str = None,
    custom_definition: Dict = None
) -> str:
    """
    Generate HTML/CSS/JS for a single Quizlet-style flip card.
    
    Args:
        metric_key: Key to look up definition (e.g., "PE_Ratio")
        value: The metric value to display
        label: Display label for the metric
        unit: Unit suffix ($, %, x, etc.)
        card_id: Unique identifier for the card
        custom_definition: Override definition if provided
    
    Returns:
        HTML string for the flip card
    """
    
    # Generate unique ID
    if card_id is None:
        card_id = hashlib.md5(f"{metric_key}_{label}".encode()).hexdigest()[:8]
    
    # Get definition
    definition = custom_definition or PROFESSIONAL_DEFINITIONS.get(metric_key, {})
    
    # Format value
    if value is None or (isinstance(value, float) and pd.isna(value)):
        formatted_value = "N/A"
        color = "#6b7280"  # Gray
    else:
        try:
            num = float(value)
            
            # Always use 2 decimal places for accuracy
            if unit == "$":
                if abs(num) >= 1e12:
                    formatted_value = f"${num/1e12:.2f}T"
                elif abs(num) >= 1e9:
                    formatted_value = f"${num/1e9:.2f}B"
                elif abs(num) >= 1e6:
                    formatted_value = f"${num/1e6:.2f}M"
                else:
                    formatted_value = f"${num:,.2f}"
            elif unit == "%":
                # Handle decimal percentages
                if abs(num) < 1 and "Ratio" not in label and "Score" not in label:
                    formatted_value = f"{num * 100:.2f}%"
                else:
                    formatted_value = f"{num:.2f}%"
            elif unit == "x":
                formatted_value = f"{num:.2f}x"
            else:
                formatted_value = f"{num:.2f}"
            
            # Determine color based on benchmarks
            benchmark = definition.get("benchmark", {})
            higher_is_better = definition.get("higher_is_better", True)
            low = benchmark.get("low")
            high = benchmark.get("high")
            
            if low is not None and high is not None:
                if higher_is_better:
                    if num >= high:
                        color = "#10b981"  # Green
                    elif num <= low:
                        color = "#ef4444"  # Red
                    else:
                        color = "#f59e0b"  # Yellow
                elif higher_is_better is False:
                    if num <= low:
                        color = "#10b981"  # Green
                    elif num >= high:
                        color = "#ef4444"  # Red
                    else:
                        color = "#f59e0b"  # Yellow
                else:
                    color = "#60a5fa"  # Blue (neutral like Beta)
            else:
                color = "#60a5fa"  # Blue default
                
        except (ValueError, TypeError):
            formatted_value = str(value) if value else "N/A"
            color = "#6b7280"
    
    # Get explanation content
    metric_name = definition.get("name", label)
    formula = definition.get("formula", "")
    explanation = definition.get("explanation", f"Measures {label.lower()}.")
    
    # Build HTML
    html = f"""
    <style>
        .flip-card-container-{card_id} {{
            perspective: 1000px;
            width: 100%;
            height: 140px;
            margin-bottom: 12px;
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
        }}
        
        .flip-card-{card_id} {{
            position: relative;
            width: 100%;
            height: 100%;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            transform-style: preserve-3d;
        }}
        
        .flip-card-container-{card_id}:hover .flip-card-{card_id} {{
            transform: scale(1.02);
        }}
        
        .flip-card-container-{card_id}.flipped .flip-card-{card_id} {{
            transform: rotateY(180deg);
        }}
        
        .flip-card-front-{card_id},
        .flip-card-back-{card_id} {{
            position: absolute;
            width: 100%;
            height: 100%;
            backface-visibility: hidden;
            -webkit-backface-visibility: hidden;
            border-radius: 12px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .flip-card-front-{card_id} {{
            background: linear-gradient(145deg, #1e293b 0%, #0f172a 100%);
            border-left: 4px solid {color};
            align-items: center;
            text-align: center;
        }}
        
        .flip-card-back-{card_id} {{
            background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%);
            border-left: 4px solid {color};
            transform: rotateY(180deg);
            text-align: left;
            overflow-y: auto;
        }}
        
        .metric-label-{card_id} {{
            color: #94a3b8;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value-{card_id} {{
            color: {color};
            font-size: 2rem;
            font-weight: 700;
            font-family: 'SF Mono', 'Roboto Mono', 'Consolas', monospace;
        }}
        
        .back-title-{card_id} {{
            color: #f1f5f9;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 6px;
        }}
        
        .back-formula-{card_id} {{
            color: #60a5fa;
            font-size: 0.75rem;
            font-family: 'SF Mono', 'Roboto Mono', 'Consolas', monospace;
            padding: 6px 8px;
            background: rgba(96, 165, 250, 0.1);
            border-radius: 4px;
            margin-bottom: 8px;
        }}
        
        .back-explanation-{card_id} {{
            color: #cbd5e1;
            font-size: 0.75rem;
            line-height: 1.5;
        }}
        
        .flip-hint-{card_id} {{
            position: absolute;
            bottom: 6px;
            right: 8px;
            color: #475569;
            font-size: 0.65rem;
            opacity: 0.6;
        }}
    </style>
    
    <div class="flip-card-container-{card_id}" onclick="this.classList.toggle('flipped')">
        <div class="flip-card-{card_id}">
            <div class="flip-card-front-{card_id}">
                <div class="metric-label-{card_id}">{label}</div>
                <div class="metric-value-{card_id}">{formatted_value}</div>
                <div class="flip-hint-{card_id}">tap to flip</div>
            </div>
            <div class="flip-card-back-{card_id}">
                <div class="back-title-{card_id}">{metric_name}</div>
                <div class="back-formula-{card_id}">{formula}</div>
                <div class="back-explanation-{card_id}">{explanation}</div>
                <div class="flip-hint-{card_id}">tap to flip</div>
            </div>
        </div>
    </div>
    """
    
    return html


def render_flip_cards(
    metrics: List[Dict],
    columns: int = 5,
    height_per_row: int = 160
) -> None:
    """
    Render multiple flip cards in a grid layout.
    
    Args:
        metrics: List of metric configurations
            Each dict: {"key": "PE_Ratio", "value": 25.5, "label": "P/E Ratio", "unit": "x"}
        columns: Number of columns in the grid
        height_per_row: Height in pixels per row of cards
    """
    
    if not metrics:
        return
    
    # Calculate rows needed
    rows = (len(metrics) + columns - 1) // columns
    total_height = rows * height_per_row + 20
    
    # Build HTML for all cards
    all_cards_html = """
    <style>
        .flip-cards-grid {
            display: grid;
            grid-template-columns: repeat(""" + str(columns) + """, 1fr);
            gap: 12px;
            padding: 8px;
        }
        
        @media (max-width: 768px) {
            .flip-cards-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 480px) {
            .flip-cards-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <div class="flip-cards-grid">
    """
    
    for i, m in enumerate(metrics):
        card_html = create_flip_card_html(
            metric_key=m.get("key", f"metric_{i}"),
            value=m.get("value"),
            label=m.get("label", f"Metric {i+1}"),
            unit=m.get("unit", ""),
            card_id=f"card_{i}_{hashlib.md5(str(m).encode()).hexdigest()[:6]}"
        )
        all_cards_html += f"<div>{card_html}</div>"
    
    all_cards_html += "</div>"
    
    # Render using Streamlit's HTML component
    components.html(all_cards_html, height=total_height, scrolling=False)


def render_dashboard_flip_cards(financials: Dict) -> None:
    """
    Render the 10 key dashboard metrics as flip cards.
    
    Args:
        financials: Financial data dictionary
    """
    
    # Extract values
    def get_value(keys, sources=None):
        if sources is None:
            sources = [financials, financials.get('market_data', {}), financials.get('info', {})]
        
        for source in sources:
            if not isinstance(source, dict):
                continue
            for key in keys if isinstance(keys, list) else [keys]:
                if key in source and source[key] is not None:
                    val = source[key]
                    if not (isinstance(val, float) and pd.isna(val)):
                        return val
        
        # Try ratios DataFrame
        ratios = financials.get('ratios', pd.DataFrame())
        if isinstance(ratios, pd.DataFrame) and not ratios.empty:
            for key in keys if isinstance(keys, list) else [keys]:
                if key in ratios.index:
                    val = ratios.loc[key].iloc[0]
                    if pd.notna(val):
                        return val
        
        return None
    
    info = financials.get('info', {})
    
    metrics = [
        {"key": "PE_Ratio", "value": get_value(['PE_Ratio', 'pe_ratio', 'trailingPE']), "label": "P/E Ratio", "unit": "x"},
        {"key": "current_price", "value": get_value(['current_price', 'currentPrice']), "label": "Price", "unit": "$"},
        {"key": "ROE", "value": get_value(['ROE', 'roe', 'returnOnEquity']), "label": "ROE", "unit": "%"},
        {"key": "Debt_to_Equity", "value": get_value(['Debt_to_Equity', 'debt_to_equity', 'debtToEquity']), "label": "Debt/Equity", "unit": "x"},
        {"key": "Gross_Margin", "value": get_value(['Gross_Margin', 'gross_margin', 'grossMargins']), "label": "Gross Margin", "unit": "%"},
        {"key": "EPS", "value": info.get('trailingEps'), "label": "EPS (TTM)", "unit": "$"},
        {"key": "market_cap", "value": info.get('marketCap') or get_value(['market_cap']), "label": "Market Cap", "unit": "$"},
        {"key": "FCF_Yield", "value": None, "label": "FCF Yield", "unit": "%"},  # Calculate if possible
        {"key": "Beta", "value": info.get('beta'), "label": "Beta", "unit": "x"},
        {"key": "Dividend_Yield", "value": info.get('dividendYield'), "label": "Div Yield", "unit": "%"},
    ]
    
    # Calculate FCF Yield if possible
    fcf = info.get('freeCashflow')
    market_cap = info.get('marketCap')
    if fcf and market_cap and market_cap > 0:
        metrics[7]["value"] = (fcf / market_cap) * 100
    
    st.markdown("### Key Metrics")
    st.caption("Click any card to see formula & professional analysis")
    
    render_flip_cards(metrics, columns=5)


# Export for use in other modules
__all__ = [
    'create_flip_card_html',
    'render_flip_cards', 
    'render_dashboard_flip_cards',
    'PROFESSIONAL_DEFINITIONS'
]

