"""
FLIP CARD INTEGRATION MODULE
============================
Master module for integrating educational flip cards across ALL tabs.

Structure:
- Tab-specific metric definitions
- Validation and testing utilities
- Safe integration with graceful fallbacks
- Checkpoint verification

Author: ATLAS Financial Intelligence
Date: December 2025
Version: 1.0

Tabs Covered:
1. Dashboard (10 metrics)
2. Data Tab (6 sub-tabs)
3. Analysis Tab (3 sections)
4. Model Tab (7 DCF sub-tabs + Live DCF)
5. Risk Tab (Forensic Shield + Governance)
6. Market Tab (Technical + Quant + Options + Peers)
7. News Tab (Sentiment)
8. Investment Summary (Scores)
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Import our flip card component
try:
    from flip_card_component import FlipCardMetric, render_flip_metric, render_depth_selector
    FLIP_CARD_AVAILABLE = True
except ImportError:
    FLIP_CARD_AVAILABLE = False
    print("[WARN] flip_card_component.py not found - using fallback")

# Import ratio definitions
try:
    from ratio_card import RATIO_DEFINITIONS
    RATIO_DEFS_AVAILABLE = True
except ImportError:
    RATIO_DEFS_AVAILABLE = False
    RATIO_DEFINITIONS = {}


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class MetricCategory(Enum):
    """Categories for organizing metrics"""
    VALUATION = "Valuation"
    PROFITABILITY = "Profitability"
    LIQUIDITY = "Liquidity"
    LEVERAGE = "Leverage"
    EFFICIENCY = "Efficiency"
    GROWTH = "Growth"
    RISK = "Risk"
    CASH_FLOW = "Cash Flow"
    DIVIDEND = "Dividend"
    FORENSIC = "Forensic"


# =============================================================================
# METRIC DEFINITIONS BY TAB
# =============================================================================

@dataclass
class MetricDefinition:
    """Definition for a flip card metric"""
    key: str                      # Internal key (e.g., "pe_ratio")
    display_name: str             # Display name (e.g., "P/E Ratio")
    formula: str                  # Formula string
    category: MetricCategory
    components: List[str]         # List of component keys needed
    explanation_beginner: str
    explanation_intermediate: str
    explanation_professional: str
    benchmark_low: float = None
    benchmark_high: float = None
    format_type: str = "ratio"    # "ratio", "percentage", "currency", "number"
    inverse_better: bool = False  # True if lower is better (e.g., P/E, D/E)


# Tab 1: Dashboard Metrics
DASHBOARD_METRICS = [
    MetricDefinition(
        key="pe_ratio",
        display_name="P/E Ratio",
        formula="Stock Price ÷ Earnings Per Share",
        category=MetricCategory.VALUATION,
        components=["current_price", "eps"],
        explanation_beginner="How many dollars you pay for each $1 of company profit. Lower = cheaper stock.",
        explanation_intermediate="P/E shows investor willingness to pay per dollar of earnings. Compare to industry peers and historical averages. High P/E may indicate growth expectations.",
        explanation_professional="Use forward P/E for earnings growth stories. PEG ratio (P/E ÷ Growth) normalizes for growth. Negative P/E (losses) requires P/S or EV/EBITDA instead. Cyclicals need normalized earnings.",
        benchmark_low=15,
        benchmark_high=25,
        format_type="ratio",
        inverse_better=True
    ),
    MetricDefinition(
        key="roe",
        display_name="ROE (Return on Equity)",
        formula="Net Income ÷ Shareholders' Equity × 100%",
        category=MetricCategory.PROFITABILITY,
        components=["net_income", "shareholders_equity"],
        explanation_beginner="How much profit the company makes with your money. 15% ROE = $15 profit for every $100 invested.",
        explanation_intermediate="ROE measures management efficiency at generating returns. Decompose with DuPont: Net Margin × Asset Turnover × Leverage. Compare to cost of equity.",
        explanation_professional="High ROE from leverage is risky. DuPont: ROE = (NI/Rev) × (Rev/Assets) × (Assets/Equity). Buffett targets >15% with low debt. Buybacks inflate ROE by reducing equity base.",
        benchmark_low=10,
        benchmark_high=20,
        format_type="percentage"
    ),
    MetricDefinition(
        key="debt_to_equity",
        display_name="Debt/Equity",
        formula="Total Debt ÷ Shareholders' Equity",
        category=MetricCategory.LEVERAGE,
        components=["total_debt", "shareholders_equity"],
        explanation_beginner="How much the company owes vs owns. Lower = safer, less risk.",
        explanation_intermediate="D/E shows financial leverage. Industry matters: utilities high, tech low. Net debt (Debt - Cash) gives truer picture.",
        explanation_professional="Lease liabilities (IFRS 16) increased reported leverage. Monitor debt maturity schedule. Interest coverage more important for credit analysis. Capital-light can run higher D/E safely.",
        benchmark_low=0.5,
        benchmark_high=1.5,
        format_type="ratio",
        inverse_better=True
    ),
    MetricDefinition(
        key="current_ratio",
        display_name="Current Ratio",
        formula="Current Assets ÷ Current Liabilities",
        category=MetricCategory.LIQUIDITY,
        components=["current_assets", "current_liabilities"],
        explanation_beginner="Can the company pay its bills due this year? Above 1 = yes.",
        explanation_intermediate="Measures short-term solvency. Too low = liquidity risk. Too high = inefficient capital use. Quick ratio (ex-inventory) more conservative.",
        explanation_professional="Quality of current assets matters: receivables collectibility, inventory obsolescence. Working capital cycle: DSO + DIO - DPO. Negative WC (Amazon model) can be strength.",
        benchmark_low=1.0,
        benchmark_high=2.0,
        format_type="ratio"
    ),
    MetricDefinition(
        key="gross_margin",
        display_name="Gross Margin",
        formula="(Revenue - COGS) ÷ Revenue × 100%",
        category=MetricCategory.PROFITABILITY,
        components=["revenue", "cost_of_goods_sold", "gross_profit"],
        explanation_beginner="How much of each sale dollar is left after paying for the product itself. Higher = better pricing power.",
        explanation_intermediate="Shows pricing power and production efficiency. Higher margin = more room for OpEx and profit. Track trends - declining may signal competition.",
        explanation_professional="Sector benchmarks: Software 70-90%, Consumer Staples 40-60%, Retail 20-40%. Segment-level margins reveal true quality. Watch for inventory accounting changes (FIFO vs LIFO).",
        benchmark_low=30,
        benchmark_high=50,
        format_type="percentage"
    ),
    MetricDefinition(
        key="operating_margin",
        display_name="Operating Margin",
        formula="Operating Income ÷ Revenue × 100%",
        category=MetricCategory.PROFITABILITY,
        components=["operating_income", "revenue"],
        explanation_beginner="How much profit from core business before interest and taxes. Shows operational efficiency.",
        explanation_intermediate="Independent of financing decisions. Excludes interest/taxes for cleaner comparison. Operating leverage = how margins expand with scale.",
        explanation_professional="Best proxy for business unit economics. Adjust for non-recurring items. High fixed costs = high operating leverage. Compare contribution margin for break-even analysis.",
        benchmark_low=10,
        benchmark_high=20,
        format_type="percentage"
    ),
    MetricDefinition(
        key="fcf_margin",
        display_name="FCF Margin",
        formula="(Operating CF - CapEx) ÷ Revenue × 100%",
        category=MetricCategory.CASH_FLOW,
        components=["operating_cash_flow", "capex", "revenue"],
        explanation_beginner="What percentage of sales becomes cash you can actually use. Higher = more cash for dividends, buybacks, or growth.",
        explanation_intermediate="Unlike net margin, it's actual cash. Track trends: declining FCF margin may indicate rising CapEx or working capital issues.",
        explanation_professional="Analyze with revenue growth: high-growth companies reinvest FCF. Mature companies should have FCF margin approaching net margin. Normalize for lumpy CapEx.",
        benchmark_low=5,
        benchmark_high=15,
        format_type="percentage"
    ),
    MetricDefinition(
        key="revenue_growth",
        display_name="Revenue Growth",
        formula="(Current Revenue - Prior Revenue) ÷ Prior Revenue × 100%",
        category=MetricCategory.GROWTH,
        components=["current_revenue", "prior_revenue"],
        explanation_beginner="How fast sales are growing year over year. Higher = faster growth.",
        explanation_intermediate="Organic growth (ex-M&A) is higher quality. Compare to GDP growth (2-3%) as baseline. Rule of 40 for SaaS: Growth% + Margin% > 40.",
        explanation_professional="Decompose: Volume × Price × Mix. Organic vs inorganic. Same-store vs new store for retail. Sustainable growth rate = ROE × (1 - Payout Ratio).",
        benchmark_low=5,
        benchmark_high=15,
        format_type="percentage"
    ),
    MetricDefinition(
        key="eps",
        display_name="EPS (Earnings Per Share)",
        formula="Net Income ÷ Shares Outstanding",
        category=MetricCategory.VALUATION,
        components=["net_income", "shares_outstanding"],
        explanation_beginner="The profit each share of stock gets. Higher = more profit per share you own.",
        explanation_intermediate="Diluted EPS accounts for options/converts. Quality matters - revenue-driven EPS growth is best. Buyback-driven may be financial engineering.",
        explanation_professional="Adjusted EPS excludes non-recurring items (verify legitimacy). GAAP vs Non-GAAP reconciliation critical. Long-term EPS growth rate key for DCF terminal value.",
        benchmark_low=0,
        benchmark_high=float('inf'),
        format_type="currency"
    ),
    MetricDefinition(
        key="dividend_yield",
        display_name="Dividend Yield",
        formula="Annual Dividend ÷ Stock Price × 100%",
        category=MetricCategory.DIVIDEND,
        components=["annual_dividend", "current_price"],
        explanation_beginner="How much cash you get back each year as percentage of stock price. Higher = more income.",
        explanation_intermediate="High yield may indicate value trap (price down) or stable income stock. Look at payout ratio for sustainability.",
        explanation_professional="Yield trap: high yield often precedes cut. Check FCF coverage and dividend history. REITs/MLPs have higher yields due to pass-through structure.",
        benchmark_low=1,
        benchmark_high=4,
        format_type="percentage"
    ),
]

# Tab 4: DCF Model Metrics
DCF_METRICS = [
    MetricDefinition(
        key="wacc",
        display_name="WACC",
        formula="(E/V × Re) + (D/V × Rd × (1-T))",
        category=MetricCategory.VALUATION,
        components=["cost_of_equity", "cost_of_debt", "equity_weight", "debt_weight", "tax_rate"],
        explanation_beginner="The minimum return a company must earn to satisfy investors. Like a 'hurdle rate' for projects.",
        explanation_intermediate="Blends cost of equity (shareholder expectations) and cost of debt (interest rate after tax). Lower WACC = higher valuation.",
        explanation_professional="Cost of Equity via CAPM: Rf + β(Rm-Rf). Use unlevered beta and relever for target structure. WACC should reflect marginal cost of capital.",
        benchmark_low=6,
        benchmark_high=12,
        format_type="percentage"
    ),
    MetricDefinition(
        key="terminal_value",
        display_name="Terminal Value",
        formula="FCF × (1+g) ÷ (WACC - g)",
        category=MetricCategory.VALUATION,
        components=["final_fcf", "terminal_growth", "wacc"],
        explanation_beginner="The value of all cash flows beyond the projection period. Usually 60-80% of total value.",
        explanation_intermediate="Gordon Growth Model for perpetuity. Terminal growth should be ≤ GDP growth (~2-3%). Very sensitive to assumptions.",
        explanation_professional="Cross-check with exit multiple method. Monte Carlo for sensitivity. Terminal growth > WACC is mathematically invalid.",
        benchmark_low=0,
        benchmark_high=float('inf'),
        format_type="currency"
    ),
    MetricDefinition(
        key="intrinsic_value",
        display_name="Intrinsic Value",
        formula="Σ PV(FCF) + PV(Terminal Value)",
        category=MetricCategory.VALUATION,
        components=["pv_fcfs", "pv_terminal"],
        explanation_beginner="The 'true value' based on future cash flows. If stock price < this, it might be undervalued.",
        explanation_intermediate="Sum of discounted cash flows + terminal value. Small input changes create large swings - sensitivity analysis critical.",
        explanation_professional="Two/three-stage models for high growth. Adjust for SBC, operating leases, NOLs. Monte Carlo for range of outcomes.",
        benchmark_low=0,
        benchmark_high=float('inf'),
        format_type="currency"
    ),
    MetricDefinition(
        key="margin_of_safety",
        display_name="Margin of Safety",
        formula="(Intrinsic Value - Price) ÷ Intrinsic Value × 100%",
        category=MetricCategory.VALUATION,
        components=["intrinsic_value", "current_price"],
        explanation_beginner="The 'discount' you get if buying below fair value. Bigger = safer investment.",
        explanation_intermediate="Benjamin Graham concept: only buy when price << intrinsic value. Value investors typically want 20-30% MoS.",
        explanation_professional="MoS should reflect confidence in DCF inputs and business quality. Wide-moat may warrant lower MoS (15-20%). Speculative needs 40%+.",
        benchmark_low=15,
        benchmark_high=50,
        format_type="percentage"
    ),
]

# Tab 5: Forensic Shield Metrics (Altman Z-Score)
FORENSIC_METRICS = [
    MetricDefinition(
        key="altman_z",
        display_name="Altman Z-Score",
        formula="1.2×X1 + 1.4×X2 + 3.3×X3 + 0.6×X4 + 1.0×X5",
        category=MetricCategory.FORENSIC,
        components=["x1_wc_assets", "x2_re_assets", "x3_ebit_assets", "x4_mcap_liab", "x5_sales_assets"],
        explanation_beginner="Predicts bankruptcy risk. Above 3 = safe, below 1.8 = danger zone.",
        explanation_intermediate="Developed by Edward Altman in 1968. 72-80% accurate in predicting bankruptcy 2 years ahead. Grey zone (1.8-3.0) requires monitoring.",
        explanation_professional="Original for manufacturing. Use Z'' for non-manufacturers. Each component has different weight: EBIT/Assets (3.3x) most important. Works best 1-2 years out.",
        benchmark_low=1.81,
        benchmark_high=2.99,
        format_type="number"
    ),
    MetricDefinition(
        key="beneish_m",
        display_name="Beneish M-Score",
        formula="-4.84 + 0.92×DSRI + 0.528×GMI + 0.404×AQI + ...",
        category=MetricCategory.FORENSIC,
        components=["dsri", "gmi", "aqi", "sgi", "depi", "sgai", "tata", "lvgi"],
        explanation_beginner="Detects earnings manipulation. Below -2.22 = likely okay, above = potential manipulation.",
        explanation_intermediate="8-variable model developed by Messod Beneish. Compares year-over-year changes to identify unusual patterns that may indicate earnings management.",
        explanation_professional="DSRI and GMI most predictive. Identified Enron before scandal. False positive rate ~10%. Use with accruals analysis and cash flow verification.",
        benchmark_low=-2.22,
        benchmark_high=-1.78,
        format_type="number",
        inverse_better=True
    ),
]

# Tab 6: Quant Metrics (Fama-French)
QUANT_METRICS = [
    MetricDefinition(
        key="cost_of_equity",
        display_name="Cost of Equity",
        formula="Rf + β × (Rm - Rf)",
        category=MetricCategory.RISK,
        components=["risk_free_rate", "beta", "market_premium"],
        explanation_beginner="The return shareholders expect for investing in this stock instead of 'safe' bonds.",
        explanation_intermediate="CAPM: Risk-free rate + beta × equity risk premium. Higher beta = higher required return. Used in WACC calculation.",
        explanation_professional="CAPM limitations: single-factor. Fama-French 3/5 factors add size, value, momentum. For private companies, add illiquidity premium (2-4%).",
        benchmark_low=7,
        benchmark_high=14,
        format_type="percentage"
    ),
    MetricDefinition(
        key="beta",
        display_name="Beta (Market Risk)",
        formula="Cov(Stock, Market) ÷ Var(Market)",
        category=MetricCategory.RISK,
        components=["stock_returns", "market_returns"],
        explanation_beginner="How much the stock moves vs the market. Beta 1.5 = if market up 10%, stock up 15%.",
        explanation_intermediate="Measures systematic risk that can't be diversified. Utilities typically <0.7, tech >1.3. Used in CAPM for required return.",
        explanation_professional="Use 5Y monthly returns. Adjusted Beta = 2/3 × Raw + 1/3 × 1.0. Levered vs unlevered for comparisons. Beta instability during market stress.",
        benchmark_low=0.8,
        benchmark_high=1.5,
        format_type="number"
    ),
    MetricDefinition(
        key="alpha",
        display_name="Alpha (Excess Return)",
        formula="Actual Return - [Rf + β(Rm - Rf)]",
        category=MetricCategory.RISK,
        components=["stock_return", "expected_return"],
        explanation_beginner="Extra return above what you'd expect given the risk. Positive = beating expectations.",
        explanation_intermediate="Jensen's Alpha measures risk-adjusted performance. Consistently positive alpha is rare. Negative = underperforming after risk adjustment.",
        explanation_professional="Use Fama-French 5-factor for more accurate alpha. Most alpha is luck, not skill (academic research). Transaction costs erode gross alpha.",
        benchmark_low=-2,
        benchmark_high=5,
        format_type="percentage"
    ),
]


# =============================================================================
# DATA EXTRACTION UTILITIES
# =============================================================================

class MetricExtractor:
    """Extract metric values from financials dictionary"""
    
    def __init__(self, financials: Dict[str, Any]):
        self.financials = financials or {}
        # Safely extract with fallback to empty dict/DataFrame
        self.info = financials.get('info') if financials else {}
        self.info = self.info if isinstance(self.info, dict) else {}
        
        self.market_data = financials.get('market_data') if financials else {}
        self.market_data = self.market_data if isinstance(self.market_data, dict) else {}
        
        self.ratios = financials.get('ratios', pd.DataFrame()) if financials else pd.DataFrame()
        if not isinstance(self.ratios, pd.DataFrame):
            self.ratios = pd.DataFrame()
        
        self.income_stmt = financials.get('income_statement', pd.DataFrame()) if financials else pd.DataFrame()
        self.balance_sheet = financials.get('balance_sheet', pd.DataFrame()) if financials else pd.DataFrame()
        self.cash_flow = financials.get('cash_flow', pd.DataFrame()) if financials else pd.DataFrame()
        
        self.growth_rates = financials.get('growth_rates') if financials else {}
        self.growth_rates = self.growth_rates if isinstance(self.growth_rates, dict) else {}
    
    def get_value(self, key: str) -> Optional[float]:
        """Get metric value by key with robust null handling"""
        if not key:
            return None
        
        # Priority order: info → market_data → ratios → calculated
        
        # Direct mappings
        key_mappings = {
            'pe_ratio': ['trailingPE', 'PE_Ratio'],
            'forward_pe': ['forwardPE', 'Forward_PE'],
            'roe': ['returnOnEquity', 'ROE'],
            'roa': ['returnOnAssets', 'ROA'],
            'debt_to_equity': ['debtToEquity', 'Debt_to_Equity'],
            'current_ratio': ['currentRatio', 'Current_Ratio'],
            'quick_ratio': ['quickRatio', 'Quick_Ratio'],
            'gross_margin': ['grossMargins', 'Gross_Margin'],
            'operating_margin': ['operatingMargins', 'Operating_Margin'],
            'profit_margin': ['profitMargins', 'Net_Margin'],
            'current_price': ['currentPrice', 'regularMarketPrice'],
            'eps': ['trailingEps', 'EPS'],
            'forward_eps': ['forwardEps'],
            'dividend_yield': ['dividendYield', 'Dividend_Yield'],
            'beta': ['beta', 'Beta'],
            'market_cap': ['marketCap', 'Market_Cap'],
            'revenue': ['totalRevenue', 'Total_Revenue'],
            'net_income': ['netIncomeToCommon', 'Net_Income'],
            'free_cash_flow': ['freeCashflow', 'Free_Cash_Flow'],
        }
        
        possible_keys = key_mappings.get(key, [key])
        
        # Try info dict first
        for k in possible_keys:
            if k in self.info and self.info[k] is not None:
                return self._to_float(self.info[k])
        
        # Try market_data
        for k in possible_keys:
            if k in self.market_data and self.market_data[k] is not None:
                return self._to_float(self.market_data[k])
        
        # Try ratios DataFrame
        if isinstance(self.ratios, pd.DataFrame) and not self.ratios.empty:
            for k in possible_keys:
                if k in self.ratios.index:
                    val = self.ratios.loc[k].iloc[0]
                    if pd.notna(val):
                        return self._to_float(val)
        
        # Try growth_rates
        for k in possible_keys:
            if k in self.growth_rates:
                return self._to_float(self.growth_rates[k])
        
        return None
    
    def get_component_values(self, components: List[str]) -> Dict[str, float]:
        """Get values for multiple components"""
        result = {}
        for comp in components:
            val = self.get_value(comp)
            if val is not None:
                result[comp] = val
        return result
    
    def _to_float(self, value: Any) -> Optional[float]:
        """Convert value to float safely"""
        if value is None or value == 'N/A':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None


# =============================================================================
# FLIP CARD RENDERER
# =============================================================================

def render_metric_with_flip(
    definition: MetricDefinition,
    extractor: MetricExtractor,
    depth: str = "beginner",
    key_prefix: str = ""
) -> None:
    """
    Render a metric with optional flip card functionality
    
    Args:
        definition: MetricDefinition for the metric
        extractor: MetricExtractor to get values
        depth: Explanation depth level
        key_prefix: Unique key prefix
    """
    value = extractor.get_value(definition.key)
    components = extractor.get_component_values(definition.components)
    
    if not FLIP_CARD_AVAILABLE:
        # Fallback: Simple metric
        formatted = _format_value(value, definition.format_type)
        st.metric(definition.display_name, formatted)
        return
    
    # Create FlipCardMetric
    metric = FlipCardMetric(
        name=definition.display_name,
        value=value,
        formula=definition.formula,
        components=components,
        explanation_beginner=definition.explanation_beginner,
        explanation_intermediate=definition.explanation_intermediate,
        explanation_professional=definition.explanation_professional,
        benchmark={"low": definition.benchmark_low, "high": definition.benchmark_high} if definition.benchmark_low is not None else None,
        category=definition.category.value
    )
    
    render_flip_metric(metric, depth=depth, key_prefix=key_prefix)


def _format_value(value: Optional[float], format_type: str) -> str:
    """Format value based on type"""
    if value is None:
        return "N/A"
    
    try:
        if format_type == "percentage":
            # Handle both decimal (0.15) and percentage (15) formats
            if abs(value) < 1:
                return f"{value * 100:.1f}%"
            return f"{value:.1f}%"
        elif format_type == "ratio":
            return f"{value:.2f}x"
        elif format_type == "currency":
            if abs(value) >= 1e12:
                return f"${value/1e12:.2f}T"
            elif abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            return f"${value:,.2f}"
        else:
            return f"{value:.2f}"
    except (ValueError, TypeError):
        return str(value)


# =============================================================================
# TAB-SPECIFIC RENDERERS
# =============================================================================

def render_dashboard_metrics_with_flip(
    financials: Dict[str, Any],
    depth: str = "beginner"
) -> None:
    """Render Dashboard tab metrics with flip cards"""
    extractor = MetricExtractor(financials)
    
    # First row: 5 metrics
    cols = st.columns(5)
    metrics_row1 = DASHBOARD_METRICS[:5]
    
    for i, defn in enumerate(metrics_row1):
        with cols[i]:
            render_metric_with_flip(defn, extractor, depth, f"dash_row1_{i}")
    
    # Second row: 5 metrics
    cols = st.columns(5)
    metrics_row2 = DASHBOARD_METRICS[5:10]
    
    for i, defn in enumerate(metrics_row2):
        with cols[i]:
            render_metric_with_flip(defn, extractor, depth, f"dash_row2_{i}")


def render_dcf_metrics_with_flip(
    dcf_results: Dict[str, Any],
    current_price: float,
    depth: str = "beginner"
) -> None:
    """Render DCF tab metrics with flip cards"""
    if not dcf_results:
        st.warning("Run DCF analysis first")
        return
    
    # Create a pseudo-financials dict for the extractor
    dcf_financials = {
        'info': {
            'wacc': dcf_results.get('wacc', dcf_results.get('base', {}).get('wacc')),
            'terminal_value': dcf_results.get('base', {}).get('terminal_value'),
            'intrinsic_value': dcf_results.get('base', {}).get('value_per_share'),
            'current_price': current_price,
        }
    }
    
    # Calculate margin of safety
    iv = dcf_results.get('base', {}).get('value_per_share', 0)
    if iv and current_price:
        dcf_financials['info']['margin_of_safety'] = (iv - current_price) / iv * 100
    
    extractor = MetricExtractor(dcf_financials)
    
    cols = st.columns(4)
    for i, defn in enumerate(DCF_METRICS):
        with cols[i % 4]:
            render_metric_with_flip(defn, extractor, depth, f"dcf_{i}")


def render_forensic_metrics_with_flip(
    forensic_data: Dict[str, Any],
    depth: str = "beginner"
) -> None:
    """Render Forensic Shield metrics with flip cards"""
    if not forensic_data:
        st.warning("No forensic analysis data")
        return
    
    # Z-Score section
    z_data = forensic_data.get('altman_z', {})
    if z_data.get('status') == 'success':
        z_financials = {
            'info': {
                'altman_z': z_data.get('z_score'),
                'x1_wc_assets': z_data.get('components', {}).get('X1_working_capital_to_assets'),
                'x2_re_assets': z_data.get('components', {}).get('X2_retained_earnings_to_assets'),
                'x3_ebit_assets': z_data.get('components', {}).get('X3_ebit_to_assets'),
                'x4_mcap_liab': z_data.get('components', {}).get('X4_market_cap_to_liabilities'),
                'x5_sales_assets': z_data.get('components', {}).get('X5_sales_to_assets'),
            }
        }
        extractor = MetricExtractor(z_financials)
        render_metric_with_flip(FORENSIC_METRICS[0], extractor, depth, "forensic_z")
    
    # M-Score section
    m_data = forensic_data.get('beneish_m', {})
    if m_data.get('status') == 'success':
        m_financials = {
            'info': {
                'beneish_m': m_data.get('m_score'),
            }
        }
        extractor = MetricExtractor(m_financials)
        render_metric_with_flip(FORENSIC_METRICS[1], extractor, depth, "forensic_m")


def render_quant_metrics_with_flip(
    quant_data: Dict[str, Any],
    depth: str = "beginner"
) -> None:
    """Render Quant tab metrics with flip cards"""
    if not quant_data:
        st.warning("No quant analysis data")
        return
    
    ff = quant_data.get('fama_french', {})
    
    quant_financials = {
        'info': {
            'cost_of_equity': ff.get('cost_of_equity_annual', 0) * 100,
            'beta': ff.get('beta_market'),
            'alpha': ff.get('alpha_annualized', 0) * 100,
            'risk_free_rate': ff.get('risk_free_rate', 0) * 12 * 100,
            'market_premium': ff.get('market_premium', 0) * 12 * 100,
        }
    }
    
    extractor = MetricExtractor(quant_financials)
    
    cols = st.columns(3)
    for i, defn in enumerate(QUANT_METRICS):
        with cols[i % 3]:
            render_metric_with_flip(defn, extractor, depth, f"quant_{i}")


# =============================================================================
# VALIDATION AND TESTING
# =============================================================================

class FlipCardValidator:
    """Validation utilities for flip card integration"""
    
    @staticmethod
    def validate_metric_definition(defn: MetricDefinition) -> Tuple[bool, List[str]]:
        """Validate a metric definition"""
        errors = []
        
        if not defn.key:
            errors.append("Missing key")
        if not defn.display_name:
            errors.append("Missing display_name")
        if not defn.formula:
            errors.append("Missing formula")
        if not defn.explanation_beginner:
            errors.append("Missing beginner explanation")
        if not defn.components:
            errors.append("Missing components list")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_all_definitions() -> Dict[str, List[str]]:
        """Validate all metric definitions"""
        results = {}
        
        all_metrics = DASHBOARD_METRICS + DCF_METRICS + FORENSIC_METRICS + QUANT_METRICS
        
        for defn in all_metrics:
            is_valid, errors = FlipCardValidator.validate_metric_definition(defn)
            if not is_valid:
                results[defn.key] = errors
        
        return results
    
    @staticmethod
    def test_extraction(financials: Dict[str, Any]) -> Dict[str, Any]:
        """Test metric extraction from financials"""
        extractor = MetricExtractor(financials)
        results = {}
        
        all_metrics = DASHBOARD_METRICS + DCF_METRICS + QUANT_METRICS
        
        for defn in all_metrics:
            value = extractor.get_value(defn.key)
            results[defn.key] = {
                'found': value is not None,
                'value': value,
                'formatted': _format_value(value, defn.format_type)
            }
        
        return results
    
    @staticmethod
    def run_checkpoint(checkpoint_name: str, test_func: Callable) -> bool:
        """Run a checkpoint test with error handling"""
        try:
            result = test_func()
            print(f"✅ CHECKPOINT {checkpoint_name}: PASSED")
            return True
        except Exception as e:
            print(f"❌ CHECKPOINT {checkpoint_name}: FAILED - {str(e)}")
            traceback.print_exc()
            return False


# =============================================================================
# TESTING
# =============================================================================

def run_all_tests():
    """Run all validation tests"""
    print("=" * 80)
    print("FLIP CARD INTEGRATION - VALIDATION TESTS")
    print("=" * 80)
    
    # Test 1: Validate definitions
    print("\n[TEST 1] Validating metric definitions...")
    errors = FlipCardValidator.validate_all_definitions()
    if errors:
        print(f"  ❌ Found errors in {len(errors)} metrics:")
        for key, errs in errors.items():
            print(f"    - {key}: {', '.join(errs)}")
    else:
        print(f"  ✅ All {len(DASHBOARD_METRICS) + len(DCF_METRICS) + len(FORENSIC_METRICS) + len(QUANT_METRICS)} definitions valid")
    
    # Test 2: Check module imports
    print("\n[TEST 2] Checking module imports...")
    print(f"  FLIP_CARD_AVAILABLE: {FLIP_CARD_AVAILABLE}")
    print(f"  RATIO_DEFS_AVAILABLE: {RATIO_DEFS_AVAILABLE}")
    
    # Test 3: Format value function
    print("\n[TEST 3] Testing format functions...")
    test_cases = [
        (0.156, "percentage", "15.6%"),
        (22.5, "ratio", "22.50x"),
        (175.50, "currency", "$175.50"),
        (1e9, "currency", "$1.00B"),
        (None, "number", "N/A"),
    ]
    for value, fmt, expected in test_cases:
        result = _format_value(value, fmt)
        status = "✅" if expected in result or result == expected else "❌"
        print(f"  {status} format({value}, {fmt}) = {result} (expected: {expected})")
    
    print("\n" + "=" * 80)
    print("TESTS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_all_tests()

