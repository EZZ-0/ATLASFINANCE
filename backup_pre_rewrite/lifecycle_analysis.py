"""
BUSINESS LIFE CYCLE ANALYSIS MODULE
====================================
Determines company life cycle stage and calculates remaining stages
before reaching maturity/stable growth phase.

Life Cycle Stages (5 Total):
    Stage 1: STARTUP      - High growth, negative/minimal FCF, high risk
    Stage 2: GROWTH       - Rapid expansion, low FCF, heavy investment
    Stage 3: EXPANSION    - Scaling, improving FCF, moderate investment
    Stage 4: MATURITY     - Stable growth, high FCF, low investment
    Stage 5: DECLINE      - Negative growth, variable FCF, minimal investment

Key Metrics Used:
    - Revenue Growth Rate (CAGR)
    - Free Cash Flow Margin
    - CapEx Intensity (CapEx/Revenue)
    - Operating Margin Trend
    - Reinvestment Rate

Author: Atlas Financial Intelligence
Date: December 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum


class LifeCycleStage(IntEnum):
    """Business life cycle stages (1-5)"""
    STARTUP = 1      # Pre-profit, hyper-growth
    GROWTH = 2       # Rapid expansion, low FCF
    EXPANSION = 3    # Scaling, improving FCF
    MATURITY = 4     # Stable, high FCF
    DECLINE = 5      # Negative growth


@dataclass
class LifeCycleResult:
    """Container for life cycle analysis results"""
    current_stage: int
    stage_name: str
    stages_to_maturity: int
    stages_remaining: int  # Before decline
    confidence: str  # HIGH, MEDIUM, LOW
    metrics_used: Dict
    stage_probabilities: Dict[str, float]
    transition_signals: Dict[str, str]
    years_in_current_stage_estimate: float
    
    def __repr__(self):
        return f"LifeCycle(Stage {self.current_stage}: {self.stage_name}, {self.stages_to_maturity} to maturity)"


# =============================================================================
# STAGE THRESHOLDS
# =============================================================================

STAGE_THRESHOLDS = {
    "STARTUP": {
        "revenue_growth_min": 0.30,      # >30% growth
        "fcf_margin_max": 0.0,           # Negative or zero FCF
        "capex_intensity_min": 0.10,     # >10% CapEx/Revenue
        "operating_margin_max": 0.05,    # <5% operating margin
    },
    "GROWTH": {
        "revenue_growth_min": 0.15,      # 15-30% growth
        "revenue_growth_max": 0.30,
        "fcf_margin_min": -0.05,         # -5% to 5% FCF margin
        "fcf_margin_max": 0.05,
        "capex_intensity_min": 0.06,     # 6-10% CapEx/Revenue
        "capex_intensity_max": 0.10,
    },
    "EXPANSION": {
        "revenue_growth_min": 0.07,      # 7-15% growth
        "revenue_growth_max": 0.15,
        "fcf_margin_min": 0.05,          # 5-12% FCF margin
        "fcf_margin_max": 0.12,
        "capex_intensity_min": 0.03,     # 3-6% CapEx/Revenue
        "capex_intensity_max": 0.06,
    },
    "MATURITY": {
        "revenue_growth_min": 0.02,      # 2-7% growth (GDP-like)
        "revenue_growth_max": 0.07,
        "fcf_margin_min": 0.12,          # >12% FCF margin
        "capex_intensity_max": 0.03,     # <3% CapEx/Revenue
    },
    "DECLINE": {
        "revenue_growth_max": 0.02,      # <2% or negative growth
        "fcf_margin_variable": True,     # Can be high (asset sales) or low
    }
}


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_lifecycle(ticker: str, financials: Optional[Dict] = None) -> LifeCycleResult:
    """
    Analyze company life cycle stage and calculate remaining stages.
    
    Args:
        ticker: Stock ticker symbol
        financials: Optional pre-extracted financials dict
        
    Returns:
        LifeCycleResult with stage analysis
    """
    print(f"\n[INFO] Analyzing life cycle for {ticker}...")
    
    # Extract metrics
    metrics = _extract_lifecycle_metrics(ticker, financials)
    
    if not metrics:
        return _default_result("Unable to extract metrics")
    
    # Calculate stage scores
    stage_scores = _calculate_stage_scores(metrics)
    
    # Determine current stage
    current_stage, stage_name, confidence = _determine_stage(stage_scores, metrics)
    
    # Calculate remaining stages
    stages_to_maturity = max(0, LifeCycleStage.MATURITY - current_stage)
    stages_remaining = max(0, LifeCycleStage.DECLINE - current_stage)
    
    # Estimate years in current stage
    years_estimate = _estimate_years_in_stage(current_stage, metrics)
    
    # Get transition signals
    transition_signals = _get_transition_signals(current_stage, metrics)
    
    # Compile result
    result = LifeCycleResult(
        current_stage=current_stage,
        stage_name=stage_name,
        stages_to_maturity=stages_to_maturity,
        stages_remaining=stages_remaining,
        confidence=confidence,
        metrics_used=metrics,
        stage_probabilities=stage_scores,
        transition_signals=transition_signals,
        years_in_current_stage_estimate=years_estimate
    )
    
    print(f"[OK] {ticker} is in Stage {current_stage} ({stage_name})")
    print(f"     Stages to Maturity: {stages_to_maturity}")
    print(f"     Stages Before Decline: {stages_remaining}")
    
    return result


def _extract_lifecycle_metrics(ticker: str, financials: Optional[Dict] = None) -> Dict:
    """Extract key metrics for life cycle analysis"""
    try:
        if financials:
            # Use provided financials
            return _extract_from_financials(financials)
        else:
            # Fetch from yfinance
            return _extract_from_yfinance(ticker)
    except Exception as e:
        print(f"[ERROR] Metric extraction failed: {e}")
        return {}


def _extract_from_yfinance(ticker: str) -> Dict:
    """Extract metrics directly from yfinance"""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Get financial statements
    income = stock.financials
    cashflow = stock.cashflow
    
    metrics = {}
    
    # Revenue Growth
    revenue_growth = info.get('revenueGrowth', 0)
    metrics['revenue_growth'] = revenue_growth if revenue_growth else 0.10  # Default 10%
    
    # Total Revenue
    total_revenue = info.get('totalRevenue', 0)
    metrics['total_revenue'] = total_revenue
    
    # Free Cash Flow
    fcf = info.get('freeCashflow', 0)
    if total_revenue and total_revenue > 0:
        metrics['fcf_margin'] = fcf / total_revenue if fcf else 0
    else:
        metrics['fcf_margin'] = 0
    
    # Operating Cash Flow
    ocf = info.get('operatingCashflow', 0)
    metrics['operating_cash_flow'] = ocf
    
    # Capital Expenditures (from cashflow statement)
    capex = 0
    if not cashflow.empty:
        for label in ['Capital Expenditure', 'Capital Expenditures', 'capitalExpenditures']:
            if label in cashflow.index:
                capex = abs(cashflow.loc[label].iloc[0])
                break
    
    if total_revenue and total_revenue > 0:
        metrics['capex_intensity'] = capex / total_revenue
    else:
        metrics['capex_intensity'] = 0.05  # Default 5%
    
    # Operating Margin
    operating_margin = info.get('operatingMargins', 0)
    metrics['operating_margin'] = operating_margin if operating_margin else 0.10
    
    # Gross Margin
    gross_margin = info.get('grossMargins', 0)
    metrics['gross_margin'] = gross_margin if gross_margin else 0.30
    
    # Net Margin
    net_margin = info.get('profitMargins', 0)
    metrics['net_margin'] = net_margin if net_margin else 0.05
    
    # Earnings Growth
    earnings_growth = info.get('earningsGrowth', 0)
    metrics['earnings_growth'] = earnings_growth if earnings_growth else 0
    
    # Calculate reinvestment rate
    # Reinvestment = (CapEx - Depreciation + Change in NWC) / NOPAT
    metrics['reinvestment_rate'] = _calculate_reinvestment_rate(metrics)
    
    # Market data for context
    metrics['market_cap'] = info.get('marketCap', 0)
    metrics['enterprise_value'] = info.get('enterpriseValue', 0)
    metrics['pe_ratio'] = info.get('trailingPE', 0)
    metrics['peg_ratio'] = info.get('pegRatio', 0)
    
    # Historical growth (if available)
    if not income.empty and 'Total Revenue' in income.index:
        revenues = income.loc['Total Revenue'].dropna()
        if len(revenues) >= 2:
            latest = revenues.iloc[0]
            oldest = revenues.iloc[-1]
            years = len(revenues) - 1
            if oldest > 0 and latest > 0:
                metrics['historical_cagr'] = (latest / oldest) ** (1/years) - 1
    
    return metrics


def _extract_from_financials(financials: Dict) -> Dict:
    """Extract metrics from provided financials dict"""
    metrics = {}
    
    # Get growth rates
    growth_rates = financials.get('growth_rates', {})
    metrics['revenue_growth'] = growth_rates.get('Total_Revenue_CAGR', 10) / 100  # Convert to decimal
    
    # Get from info
    info = financials.get('info', {})
    metrics['total_revenue'] = info.get('totalRevenue', 0)
    
    # FCF Margin
    fcf = info.get('freeCashflow', 0)
    if metrics['total_revenue'] > 0:
        metrics['fcf_margin'] = fcf / metrics['total_revenue']
    else:
        metrics['fcf_margin'] = 0
    
    # CapEx Intensity
    cashflow = financials.get('cash_flow', pd.DataFrame())
    capex = 0
    if not cashflow.empty:
        for label in ['Capital Expenditure', 'Capital Expenditures', 'Capex']:
            if label in cashflow.index:
                capex = abs(cashflow.loc[label].iloc[0])
                break
    
    if metrics['total_revenue'] > 0:
        metrics['capex_intensity'] = capex / metrics['total_revenue']
    else:
        metrics['capex_intensity'] = 0.05
    
    # Operating Margin
    metrics['operating_margin'] = info.get('operatingMargins', 0.10)
    metrics['gross_margin'] = info.get('grossMargins', 0.30)
    
    # Reinvestment rate
    metrics['reinvestment_rate'] = _calculate_reinvestment_rate(metrics)
    
    return metrics


def _calculate_reinvestment_rate(metrics: Dict) -> float:
    """
    Calculate reinvestment rate (how much of earnings go back into business)
    Higher reinvestment = earlier stage, Lower = more mature
    """
    capex_intensity = metrics.get('capex_intensity', 0.05)
    fcf_margin = metrics.get('fcf_margin', 0)
    operating_margin = metrics.get('operating_margin', 0.10)
    
    if operating_margin > 0:
        # Simplified: (CapEx as % of revenue) / (Operating Margin)
        # High ratio = reinvesting most of profits
        reinvestment = capex_intensity / operating_margin
        return min(reinvestment, 2.0)  # Cap at 200%
    
    return 0.5  # Default


def _calculate_stage_scores(metrics: Dict) -> Dict[str, float]:
    """
    Calculate probability scores for each stage (0-100%)
    Uses weighted multi-factor scoring
    """
    scores = {
        "STARTUP": 0,
        "GROWTH": 0,
        "EXPANSION": 0,
        "MATURITY": 0,
        "DECLINE": 0
    }
    
    revenue_growth = metrics.get('revenue_growth', 0)
    fcf_margin = metrics.get('fcf_margin', 0)
    capex_intensity = metrics.get('capex_intensity', 0.05)
    operating_margin = metrics.get('operating_margin', 0.10)
    reinvestment_rate = metrics.get('reinvestment_rate', 0.5)
    
    # STARTUP scoring (weight: growth 40%, FCF 30%, CapEx 30%)
    if revenue_growth > 0.30:
        scores["STARTUP"] += 40
    elif revenue_growth > 0.20:
        scores["STARTUP"] += 25
    
    if fcf_margin < 0:
        scores["STARTUP"] += 30
    elif fcf_margin < 0.02:
        scores["STARTUP"] += 15
    
    if capex_intensity > 0.10:
        scores["STARTUP"] += 30
    elif capex_intensity > 0.08:
        scores["STARTUP"] += 15
    
    # GROWTH scoring
    if 0.15 <= revenue_growth <= 0.30:
        scores["GROWTH"] += 35
    elif 0.12 <= revenue_growth < 0.15:
        scores["GROWTH"] += 25
    elif revenue_growth > 0.30:
        scores["GROWTH"] += 15  # Could be late startup
    
    if 0 <= fcf_margin <= 0.05:
        scores["GROWTH"] += 30
    elif -0.05 <= fcf_margin < 0:
        scores["GROWTH"] += 20
    
    if 0.06 <= capex_intensity <= 0.10:
        scores["GROWTH"] += 35
    elif 0.05 <= capex_intensity < 0.06:
        scores["GROWTH"] += 20
    
    # EXPANSION scoring
    if 0.07 <= revenue_growth <= 0.15:
        scores["EXPANSION"] += 35
    elif 0.05 <= revenue_growth < 0.07:
        scores["EXPANSION"] += 20
    
    if 0.05 <= fcf_margin <= 0.12:
        scores["EXPANSION"] += 35
    elif 0.03 <= fcf_margin < 0.05:
        scores["EXPANSION"] += 20
    
    if 0.03 <= capex_intensity <= 0.06:
        scores["EXPANSION"] += 30
    elif 0.02 <= capex_intensity < 0.03:
        scores["EXPANSION"] += 15
    
    # MATURITY scoring
    if 0.02 <= revenue_growth <= 0.07:
        scores["MATURITY"] += 35
    elif 0.01 <= revenue_growth < 0.02:
        scores["MATURITY"] += 20
    
    if fcf_margin > 0.12:
        scores["MATURITY"] += 40
    elif fcf_margin > 0.08:
        scores["MATURITY"] += 25
    
    if capex_intensity < 0.03:
        scores["MATURITY"] += 25
    elif capex_intensity < 0.04:
        scores["MATURITY"] += 15
    
    # DECLINE scoring
    if revenue_growth < 0.02:
        scores["DECLINE"] += 40
    if revenue_growth < 0:
        scores["DECLINE"] += 30
    
    if capex_intensity < 0.02:
        scores["DECLINE"] += 20
    
    if operating_margin < 0.05:
        scores["DECLINE"] += 20
    
    # Normalize scores to percentages
    total = sum(scores.values())
    if total > 0:
        for stage in scores:
            scores[stage] = round((scores[stage] / total) * 100, 1)
    
    return scores


def _determine_stage(stage_scores: Dict[str, float], metrics: Dict) -> Tuple[int, str, str]:
    """
    Determine the most likely current stage
    
    Returns:
        Tuple of (stage_number, stage_name, confidence_level)
    """
    # Find highest scoring stage
    max_stage = max(stage_scores, key=stage_scores.get)
    max_score = stage_scores[max_stage]
    
    # Map to stage number
    stage_map = {
        "STARTUP": (1, "Startup"),
        "GROWTH": (2, "Growth"),
        "EXPANSION": (3, "Expansion"),
        "MATURITY": (4, "Maturity"),
        "DECLINE": (5, "Decline")
    }
    
    stage_num, stage_name = stage_map[max_stage]
    
    # Determine confidence based on score differential
    sorted_scores = sorted(stage_scores.values(), reverse=True)
    if len(sorted_scores) >= 2:
        score_gap = sorted_scores[0] - sorted_scores[1]
        
        if score_gap > 20:
            confidence = "HIGH"
        elif score_gap > 10:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"
    else:
        confidence = "MEDIUM"
    
    return stage_num, stage_name, confidence


def _estimate_years_in_stage(current_stage: int, metrics: Dict) -> float:
    """
    Estimate how many years company will remain in current stage
    Based on historical patterns and current metrics
    """
    revenue_growth = metrics.get('revenue_growth', 0)
    fcf_margin = metrics.get('fcf_margin', 0)
    
    # Base estimates by stage
    base_years = {
        1: 2.0,   # Startup: ~2 years
        2: 3.0,   # Growth: ~3 years
        3: 4.0,   # Expansion: ~4 years
        4: 10.0,  # Maturity: ~10+ years
        5: 5.0    # Decline: ~5 years
    }
    
    years = base_years.get(current_stage, 3.0)
    
    # Adjust based on metrics
    if current_stage == 2:  # Growth
        # Higher growth = longer in stage
        if revenue_growth > 0.25:
            years += 1.5
        elif revenue_growth > 0.20:
            years += 0.5
    elif current_stage == 3:  # Expansion
        # Higher FCF improvement = faster transition to maturity
        if fcf_margin > 0.10:
            years -= 1.0
        elif fcf_margin > 0.07:
            years -= 0.5
    
    return round(max(years, 1.0), 1)


def _get_transition_signals(current_stage: int, metrics: Dict) -> Dict[str, str]:
    """
    Get signals indicating transition to next stage
    """
    signals = {}
    
    revenue_growth = metrics.get('revenue_growth', 0)
    fcf_margin = metrics.get('fcf_margin', 0)
    capex_intensity = metrics.get('capex_intensity', 0.05)
    
    if current_stage == 1:  # Startup → Growth
        signals['growth_deceleration'] = "WATCH" if revenue_growth < 0.35 else "NOT YET"
        signals['fcf_positive'] = "TRIGGERED" if fcf_margin > 0 else "PENDING"
        signals['capex_moderation'] = "TRIGGERED" if capex_intensity < 0.10 else "PENDING"
        
    elif current_stage == 2:  # Growth → Expansion
        signals['growth_slowing'] = "TRIGGERED" if revenue_growth < 0.15 else "PENDING"
        signals['fcf_improving'] = "TRIGGERED" if fcf_margin > 0.05 else "PENDING"
        signals['capex_declining'] = "TRIGGERED" if capex_intensity < 0.06 else "PENDING"
        
    elif current_stage == 3:  # Expansion → Maturity
        signals['growth_stabilizing'] = "TRIGGERED" if revenue_growth < 0.10 else "PENDING"
        signals['fcf_strong'] = "TRIGGERED" if fcf_margin > 0.12 else "PENDING"
        signals['capex_minimal'] = "TRIGGERED" if capex_intensity < 0.03 else "PENDING"
        
    elif current_stage == 4:  # Maturity → Decline
        signals['growth_stalling'] = "WARNING" if revenue_growth < 0.03 else "STABLE"
        signals['margin_pressure'] = "WARNING" if metrics.get('operating_margin', 0.10) < 0.08 else "STABLE"
        
    elif current_stage == 5:  # Decline
        signals['turnaround_potential'] = "POSSIBLE" if fcf_margin > 0.05 else "UNLIKELY"
    
    return signals


def _default_result(error_message: str) -> LifeCycleResult:
    """Return default result when analysis fails"""
    return LifeCycleResult(
        current_stage=3,
        stage_name="Unknown (Default: Expansion)",
        stages_to_maturity=1,
        stages_remaining=2,
        confidence="LOW",
        metrics_used={"error": error_message},
        stage_probabilities={"EXPANSION": 100.0},
        transition_signals={},
        years_in_current_stage_estimate=3.0
    )


# =============================================================================
# VISUALIZATION & REPORTING
# =============================================================================

def get_lifecycle_summary(result: LifeCycleResult) -> str:
    """Generate text summary of life cycle analysis"""
    
    summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                  BUSINESS LIFE CYCLE ANALYSIS                 ║
╠══════════════════════════════════════════════════════════════╣
║  CURRENT STAGE: {result.current_stage} - {result.stage_name.upper():^20}               ║
║  CONFIDENCE: {result.confidence:^10}                                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ STAGE PROGRESSION:                                      │ ║
║  │                                                         │ ║
║  │   [1]       [2]       [3]       [4]       [5]          │ ║
║  │ Startup → Growth → Expansion → Maturity → Decline      │ ║
║  │   {'●' if result.current_stage == 1 else '○'}           {'●' if result.current_stage == 2 else '○'}          {'●' if result.current_stage == 3 else '○'}          {'●' if result.current_stage == 4 else '○'}          {'●' if result.current_stage == 5 else '○'}         │ ║
║  │                                                         │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                              ║
║  STAGES TO MATURITY:        {result.stages_to_maturity}                              ║
║  STAGES BEFORE DECLINE:     {result.stages_remaining}                              ║
║  EST. YEARS IN STAGE:       {result.years_in_current_stage_estimate}                            ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  STAGE PROBABILITIES:                                        ║
"""
    
    for stage, prob in result.stage_probabilities.items():
        bar_length = int(prob / 5)  # Scale to max 20 chars
        bar = '█' * bar_length + '░' * (20 - bar_length)
        summary += f"║    {stage:12}: {bar} {prob:5.1f}%   ║\n"
    
    summary += """╠══════════════════════════════════════════════════════════════╣
║  TRANSITION SIGNALS:                                         ║
"""
    
    for signal, status in result.transition_signals.items():
        status_icon = "✓" if status == "TRIGGERED" else "○" if status == "PENDING" else "⚠"
        summary += f"║    {status_icon} {signal:25}: {status:12}       ║\n"
    
    summary += """╚══════════════════════════════════════════════════════════════╝
"""
    
    return summary


def get_lifecycle_for_dcf(result: LifeCycleResult) -> Dict:
    """
    Get DCF-relevant parameters based on life cycle stage
    
    Returns suggested DCF assumptions based on stage
    """
    stage = result.current_stage
    
    dcf_params = {
        1: {  # Startup
            "projection_years": 10,
            "high_growth_years": 5,
            "fade_period_years": 3,
            "terminal_growth": 0.025,
            "discount_rate_premium": 0.04,  # Add to base WACC
            "suggested_growth_y1_y3": (0.25, 0.35),
            "suggested_growth_y4_y5": (0.15, 0.25),
            "capex_fade": "High to Moderate (10% → 5%)",
            "fcf_conversion_expectation": "Negative → Low Positive"
        },
        2: {  # Growth
            "projection_years": 7,
            "high_growth_years": 4,
            "fade_period_years": 2,
            "terminal_growth": 0.025,
            "discount_rate_premium": 0.02,
            "suggested_growth_y1_y3": (0.15, 0.25),
            "suggested_growth_y4_y5": (0.10, 0.15),
            "capex_fade": "Moderate to Low (6% → 4%)",
            "fcf_conversion_expectation": "Low → Moderate (5-10%)"
        },
        3: {  # Expansion
            "projection_years": 5,
            "high_growth_years": 3,
            "fade_period_years": 2,
            "terminal_growth": 0.025,
            "discount_rate_premium": 0.01,
            "suggested_growth_y1_y3": (0.08, 0.15),
            "suggested_growth_y4_y5": (0.05, 0.10),
            "capex_fade": "Low to Maintenance (4% → 2%)",
            "fcf_conversion_expectation": "Moderate → Strong (10-15%)"
        },
        4: {  # Maturity
            "projection_years": 5,
            "high_growth_years": 0,
            "fade_period_years": 0,
            "terminal_growth": 0.02,
            "discount_rate_premium": 0.0,
            "suggested_growth_y1_y3": (0.03, 0.07),
            "suggested_growth_y4_y5": (0.02, 0.05),
            "capex_fade": "Maintenance Only (2-3%)",
            "fcf_conversion_expectation": "Strong & Stable (15%+)"
        },
        5: {  # Decline
            "projection_years": 5,
            "high_growth_years": 0,
            "fade_period_years": 0,
            "terminal_growth": 0.01,  # Below GDP
            "discount_rate_premium": 0.03,
            "suggested_growth_y1_y3": (-0.05, 0.02),
            "suggested_growth_y4_y5": (-0.05, 0.0),
            "capex_fade": "Minimal (1-2%)",
            "fcf_conversion_expectation": "Variable - may be high from asset sales"
        }
    }
    
    return dcf_params.get(stage, dcf_params[3])  # Default to Expansion


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("TESTING LIFE CYCLE ANALYSIS MODULE")
    print("=" * 70)
    
    # Test with FIVE (Five Below)
    test_tickers = ["FIVE", "AAPL", "TSLA", "WMT"]
    
    for ticker in test_tickers:
        print(f"\n{'='*50}")
        print(f"Analyzing: {ticker}")
        print("=" * 50)
        
        result = analyze_lifecycle(ticker)
        print(get_lifecycle_summary(result))
        
        # Show DCF parameters
        dcf_params = get_lifecycle_for_dcf(result)
        print("\nSuggested DCF Parameters:")
        for key, value in dcf_params.items():
            print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)


