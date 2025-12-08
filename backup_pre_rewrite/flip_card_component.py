"""
FLIP CARD COMPONENT - EDUCATIONAL METRIC DISPLAY
=================================================
Click on any metric to reveal:
1. The FORMULA used
2. The ACTUAL NUMBERS plugged in
3. 3-depth explanations (Beginner → Intermediate → CFA)
4. Industry comparison

Usage:
    from flip_card_component import FlipCardMetric, render_flip_metric

Author: ATLAS Financial Intelligence
Date: December 2025
"""

import streamlit as st
from typing import Dict, Any, Optional, List, Union
import pandas as pd

# Import ratio definitions (40+ ratios with formulas)
try:
    from ratio_card import RATIO_DEFINITIONS
    RATIO_DEFS_AVAILABLE = True
except ImportError:
    RATIO_DEFS_AVAILABLE = False
    RATIO_DEFINITIONS = {}


class FlipCardMetric:
    """
    Educational flip card for any financial metric
    
    Shows:
    - Front: Value with visual indicator
    - Back (on click): Formula + calculation + explanation
    """
    
    # Industry benchmarks for common metrics
    INDUSTRY_BENCHMARKS = {
        'pe_ratio': {'sp500': 22, 'growth': 35, 'value': 15},
        'roe': {'good': 0.15, 'excellent': 0.20, 'weak': 0.10},
        'debt_to_equity': {'conservative': 0.5, 'moderate': 1.0, 'aggressive': 2.0},
        'current_ratio': {'healthy': 1.5, 'minimum': 1.0},
        'gross_margin': {'high': 0.50, 'moderate': 0.30, 'low': 0.15},
        'operating_margin': {'high': 0.20, 'moderate': 0.10, 'low': 0.05},
        'fcf_margin': {'excellent': 0.15, 'good': 0.10, 'weak': 0.05},
    }
    
    def __init__(
        self,
        name: str,
        value: Union[float, int, str],
        formula: str = None,
        components: Dict[str, float] = None,
        explanation_beginner: str = None,
        explanation_intermediate: str = None,
        explanation_professional: str = None,
        benchmark: Dict = None,
        category: str = "General"
    ):
        """
        Initialize flip card metric
        
        Args:
            name: Display name (e.g., "P/E Ratio")
            value: The calculated value
            formula: Formula string (e.g., "Price ÷ EPS")
            components: Dict of component values {"Price": 175.50, "EPS": 7.80}
            explanation_*: 3-depth explanations
            benchmark: {"low": 15, "high": 25} or use INDUSTRY_BENCHMARKS
            category: "Valuation", "Profitability", etc.
        """
        self.name = name
        self.value = value
        self.formula = formula
        self.components = components or {}
        self.explanations = {
            'beginner': explanation_beginner or "A financial metric.",
            'intermediate': explanation_intermediate or explanation_beginner or "A financial metric.",
            'professional': explanation_professional or explanation_intermediate or "A financial metric.",
        }
        self.benchmark = benchmark
        self.category = category
        
        # Try to get from ratio_card definitions if not provided
        self._load_from_definitions()
    
    def _load_from_definitions(self):
        """Load missing data from ratio_card.py definitions"""
        if not RATIO_DEFS_AVAILABLE:
            return
        
        # Map common names to ratio_card keys
        name_mapping = {
            'P/E Ratio': 'PE_Ratio',
            'PE Ratio': 'PE_Ratio',
            'P/B Ratio': 'PB_Ratio',
            'P/S Ratio': 'PS_Ratio',
            'EV/EBITDA': 'EV_EBITDA',
            'ROE': 'ROE',
            'ROA': 'ROA',
            'ROIC': 'ROIC',
            'Gross Margin': 'Gross_Margin',
            'Operating Margin': 'Operating_Margin',
            'Net Margin': 'Net_Margin',
            'Debt/Equity': 'Debt_to_Equity',
            'Current Ratio': 'Current_Ratio',
            'Quick Ratio': 'Quick_Ratio',
            'Beta': 'Beta',
            'FCF Yield': 'FCF_Yield',
            'Forward P/E': 'Forward_PE',
            'PEG Ratio': 'PEG_Ratio',
            'WACC': 'WACC',
        }
        
        ratio_key = name_mapping.get(self.name)
        if ratio_key and ratio_key in RATIO_DEFINITIONS:
            defn = RATIO_DEFINITIONS[ratio_key]
            
            if not self.formula:
                self.formula = defn.get('equation_formula', defn.get('equation', ''))
            
            if self.explanations['beginner'] == "A financial metric.":
                self.explanations = defn.get('explanations', self.explanations)
            
            if not self.benchmark:
                self.benchmark = defn.get('benchmark')
            
            if not self.category or self.category == "General":
                self.category = defn.get('category', 'General')
    
    def get_color(self) -> str:
        """Determine color based on value vs benchmark"""
        if not self.benchmark or self.value is None or self.value == 'N/A':
            return "#60a5fa"  # Blue default
        
        try:
            val = float(self.value)
            low = self.benchmark.get('low', float('-inf'))
            high = self.benchmark.get('high', float('inf'))
            
            # Some ratios: lower is better (P/E, D/E)
            inverse_better = self.name in ['P/E Ratio', 'PE Ratio', 'P/B Ratio', 
                                           'Debt/Equity', 'EV/EBITDA', 'PEG Ratio']
            
            if inverse_better:
                if val < low:
                    return "#22c55e"  # Green (good)
                elif val > high:
                    return "#ef4444"  # Red (bad)
            else:
                if val > high:
                    return "#22c55e"  # Green (good)
                elif val < low:
                    return "#ef4444"  # Red (bad)
            
            return "#f59e0b"  # Yellow (neutral)
        except (ValueError, TypeError):
            return "#60a5fa"
    
    def format_value(self) -> str:
        """Format value for display"""
        if self.value is None or self.value == 'N/A':
            return "N/A"
        
        try:
            val = float(self.value)
            
            # Percentages
            if 'Margin' in self.name or 'ROE' in self.name or 'ROA' in self.name or 'Yield' in self.name:
                if abs(val) < 1:
                    return f"{val * 100:.1f}%"
                return f"{val:.1f}%"
            
            # Ratios
            if 'Ratio' in self.name or '/' in self.name or 'EBITDA' in self.name:
                return f"{val:.2f}x"
            
            # Large numbers
            if abs(val) >= 1e12:
                return f"${val/1e12:.2f}T"
            if abs(val) >= 1e9:
                return f"${val/1e9:.2f}B"
            if abs(val) >= 1e6:
                return f"${val/1e6:.2f}M"
            
            return f"{val:.2f}"
        except (ValueError, TypeError):
            return str(self.value)
    
    def get_calculation_string(self) -> str:
        """Build string showing actual calculation"""
        if not self.components:
            return ""
        
        parts = []
        for name, val in self.components.items():
            if val is None:
                parts.append(f"{name}: N/A")
            elif abs(val) >= 1e9:
                parts.append(f"{name}: ${val/1e9:.2f}B")
            elif abs(val) >= 1e6:
                parts.append(f"{name}: ${val/1e6:.2f}M")
            elif abs(val) < 1 and val != 0:
                parts.append(f"{name}: {val:.4f}")
            else:
                parts.append(f"{name}: ${val:,.2f}" if 'price' in name.lower() else f"{name}: {val:,.2f}")
        
        return " | ".join(parts)


def render_flip_metric(
    metric: FlipCardMetric,
    depth: str = "beginner",
    show_formula: bool = True,
    key_prefix: str = ""
) -> None:
    """
    Render an interactive flip card metric in Streamlit
    
    Args:
        metric: FlipCardMetric instance
        depth: "beginner", "intermediate", or "professional"
        show_formula: Whether to show formula on flip
        key_prefix: Unique key prefix for this instance
    """
    
    unique_key = f"{key_prefix}_{metric.name}".replace(" ", "_").replace("/", "_")
    
    # Initialize state
    if f"flip_{unique_key}" not in st.session_state:
        st.session_state[f"flip_{unique_key}"] = False
    
    is_flipped = st.session_state[f"flip_{unique_key}"]
    color = metric.get_color()
    formatted_value = metric.format_value()
    
    # Create the card
    if not is_flipped:
        # FRONT OF CARD
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #1a1a2e, #0f0f1a);
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
            border-left: 4px solid {color};
            cursor: pointer;
            transition: all 0.3s ease;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: #6b7280; font-size: 0.75rem; text-transform: uppercase;">{metric.category}</span>
                    <h4 style="color: #e2e8f0; margin: 4px 0; font-size: 1rem;">{metric.name}</h4>
                </div>
                <div style="text-align: right;">
                    <div style="color: {color}; font-size: 1.5rem; font-weight: 700;">{formatted_value}</div>
                    <span style="color: #6b7280; font-size: 0.7rem;">Click to learn more</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📖 Show Formula", key=f"btn_{unique_key}", use_container_width=True):
            st.session_state[f"flip_{unique_key}"] = True
            st.rerun()
    
    else:
        # BACK OF CARD (FLIPPED)
        calculation = metric.get_calculation_string()
        explanation = metric.explanations.get(depth, metric.explanations['beginner'])
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(145deg, #0f172a, #1e293b);
            border-radius: 12px;
            padding: 20px;
            margin: 8px 0;
            border: 1px solid #334155;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h4 style="color: #e2e8f0; margin: 0;">{metric.name}</h4>
                <span style="color: {color}; font-size: 1.3rem; font-weight: 700;">{formatted_value}</span>
            </div>
            
            <!-- Formula -->
            <div style="background: #0f172a; padding: 12px; border-radius: 8px; margin: 12px 0; border: 1px solid #1e3a5f;">
                <div style="color: #64748b; font-size: 0.75rem; margin-bottom: 4px;">FORMULA</div>
                <div style="color: #60a5fa; font-family: 'Courier New', monospace; font-size: 0.95rem;">
                    {metric.formula or "Formula not available"}
                </div>
            </div>
            
            <!-- Calculation with actual numbers -->
            {"<div style='background: #1a1a2e; padding: 10px; border-radius: 6px; margin: 12px 0;'><div style='color: #64748b; font-size: 0.7rem;'>YOUR CALCULATION</div><div style='color: #a5b4fc; font-size: 0.85rem;'>" + calculation + "</div></div>" if calculation else ""}
            
            <!-- Explanation -->
            <div style="color: #94a3b8; font-size: 0.85rem; line-height: 1.6; margin-top: 12px; padding-top: 12px; border-top: 1px solid #334155;">
                {explanation}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("← Back", key=f"back_{unique_key}", use_container_width=True):
            st.session_state[f"flip_{unique_key}"] = False
            st.rerun()


def render_metrics_grid(
    metrics: List[FlipCardMetric],
    depth: str = "beginner",
    columns: int = 2
) -> None:
    """
    Render a grid of flip card metrics
    
    Args:
        metrics: List of FlipCardMetric instances
        depth: Explanation depth level
        columns: Number of columns in grid
    """
    cols = st.columns(columns)
    
    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            render_flip_metric(metric, depth=depth, key_prefix=f"grid_{i}")


def render_depth_selector(key: str = "depth_selector") -> str:
    """Render depth level selector"""
    return st.radio(
        "Explanation Depth",
        options=["beginner", "intermediate", "professional"],
        format_func=lambda x: {
            "beginner": "🎓 Beginner",
            "intermediate": "📊 Intermediate", 
            "professional": "🎯 CFA-Level"
        }.get(x, x),
        horizontal=True,
        key=key
    )


# =============================================================================
# HELPER: Create FlipCardMetrics from Financials Dict
# =============================================================================

def create_metrics_from_financials(financials: Dict) -> List[FlipCardMetric]:
    """
    Auto-create flip card metrics from extracted financials
    
    Args:
        financials: Dictionary from USAFinancialExtractor
    
    Returns:
        List of FlipCardMetric instances
    """
    metrics = []
    
    # Extract data
    info = financials.get('info', {})
    market_data = financials.get('market_data', {})
    ratios = financials.get('ratios', pd.DataFrame())
    
    def get_ratio(key):
        if isinstance(ratios, pd.DataFrame) and not ratios.empty and key in ratios.index:
            return ratios.loc[key].iloc[0]
        return None
    
    # P/E Ratio
    pe = info.get('trailingPE') or get_ratio('PE_Ratio')
    if pe:
        price = market_data.get('current_price') or info.get('currentPrice')
        eps = info.get('trailingEps')
        metrics.append(FlipCardMetric(
            name="P/E Ratio",
            value=pe,
            formula="Stock Price ÷ Earnings Per Share",
            components={"Price": price, "EPS": eps} if price and eps else None,
            category="Valuation",
            benchmark={"low": 15, "high": 25}
        ))
    
    # ROE
    roe = get_ratio('ROE') or info.get('returnOnEquity')
    if roe:
        net_income = get_ratio('Net_Income')
        equity = get_ratio('Shareholders_Equity') or get_ratio('Total Stockholders\' Equity')
        metrics.append(FlipCardMetric(
            name="ROE",
            value=roe,
            formula="Net Income ÷ Shareholders' Equity × 100%",
            components={"Net Income": net_income, "Equity": equity} if net_income and equity else None,
            category="Profitability",
            benchmark={"low": 0.10, "high": 0.20}
        ))
    
    # Debt/Equity
    de = get_ratio('Debt_to_Equity') or info.get('debtToEquity')
    if de and de > 0:
        # Convert if it's a percentage
        if de > 10:
            de = de / 100
        metrics.append(FlipCardMetric(
            name="Debt/Equity",
            value=de,
            formula="Total Debt ÷ Shareholders' Equity",
            category="Leverage",
            benchmark={"low": 0.5, "high": 1.5}
        ))
    
    # Gross Margin
    gm = get_ratio('Gross_Margin') or info.get('grossMargins')
    if gm:
        metrics.append(FlipCardMetric(
            name="Gross Margin",
            value=gm,
            formula="(Revenue - Cost of Goods Sold) ÷ Revenue × 100%",
            category="Profitability",
            benchmark={"low": 0.30, "high": 0.50}
        ))
    
    # Current Ratio
    cr = get_ratio('Current_Ratio') or info.get('currentRatio')
    if cr:
        metrics.append(FlipCardMetric(
            name="Current Ratio",
            value=cr,
            formula="Current Assets ÷ Current Liabilities",
            category="Liquidity",
            benchmark={"low": 1.0, "high": 2.0}
        ))
    
    # Free Cash Flow Margin
    fcf = info.get('freeCashflow')
    revenue = get_ratio('Total_Revenue') or get_ratio('Total Revenue')
    if fcf and revenue:
        fcf_margin = fcf / revenue
        metrics.append(FlipCardMetric(
            name="FCF Margin",
            value=fcf_margin,
            formula="(Operating Cash Flow - CapEx) ÷ Revenue × 100%",
            components={"FCF": fcf, "Revenue": revenue},
            category="Profitability",
            benchmark={"low": 0.05, "high": 0.15}
        ))
    
    return metrics


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("FLIP CARD COMPONENT - TEST")
    print("=" * 80)
    
    # Create test metric
    test_metric = FlipCardMetric(
        name="P/E Ratio",
        value=22.5,
        formula="Stock Price ÷ Earnings Per Share",
        components={"Price": 175.50, "EPS": 7.80},
        explanation_beginner="How many dollars you pay for each $1 of profit.",
        explanation_intermediate="The Price-to-Earnings ratio shows investor willingness to pay per dollar of earnings.",
        explanation_professional="Forward P/E uses expected earnings. Consider PEG for growth-adjusted valuation.",
        benchmark={"low": 15, "high": 25},
        category="Valuation"
    )
    
    print(f"Metric: {test_metric.name}")
    print(f"Value: {test_metric.format_value()}")
    print(f"Color: {test_metric.get_color()}")
    print(f"Calculation: {test_metric.get_calculation_string()}")
    print(f"Formula: {test_metric.formula}")
    
    print("\n✅ Component ready for Streamlit integration")
    print("=" * 80)

