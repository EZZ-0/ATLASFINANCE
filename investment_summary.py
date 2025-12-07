"""
INVESTMENT SUMMARY MODULE
=========================
One-page investment decision sheet with:
- Bull/Bear case (auto-generated from financial signals)
- Key metrics dashboard
- Risk assessment heatmap
- Valuation range (bear/base/bull)
- Industry positioning
- Red flags detection

This module provides everything an investor needs to make a decision on one screen.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple, Any

# Import UI enhancement components with fallback
try:
    from ui_components import render_gauge, render_radar_chart, ECHARTS_AVAILABLE
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False
    ECHARTS_AVAILABLE = False
    def render_gauge(*args, **kwargs):
        pass
    def render_radar_chart(*args, **kwargs):
        pass

class InvestmentSummaryGenerator:
    """
    Generate comprehensive investment summary from financial data
    """
    
    def __init__(self, financials: Dict):
        """
        Initialize with extracted financials dictionary
        
        Args:
            financials: Dictionary from USAFinancialExtractor
        """
        self.financials = financials
        self.ticker = financials.get('ticker', 'N/A')
        self.company_name = financials.get('company_name', 'N/A')
        self.ratios = financials.get('ratios', pd.DataFrame())
        self.growth_rates = financials.get('growth_rates', {})
        self.income_stmt = financials.get('income_statement', pd.DataFrame())
        self.balance_sheet = financials.get('balance_sheet', pd.DataFrame())
        self.market_data = financials.get('market_data', {})
        
    # ==========================================
    # BULL/BEAR CASE GENERATION
    # ==========================================
    
    def generate_bull_case(self) -> List[str]:
        """
        Auto-generate bull case bullets from positive financial signals
        
        Returns:
            List of 3 bull case points
        """
        bull_points = []
        
        # Helper to get ratio value
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        # Signal 1: Profitability
        roe = get_ratio('ROE')
        if roe and roe > 0.15:  # ROE > 15%
            bull_points.append(f"Strong profitability: ROE of {roe*100:.1f}%, indicating efficient use of shareholder capital")
        
        # Signal 2: Margins
        gross_margin = get_ratio('Gross_Margin')
        operating_margin = get_ratio('Operating_Margin')
        if gross_margin and gross_margin > 0.30:  # Gross margin > 30%
            bull_points.append(f"Healthy margins: Gross margin of {gross_margin*100:.1f}%, demonstrating pricing power and competitive advantage")
        elif operating_margin and operating_margin > 0.15:
            bull_points.append(f"Strong operating efficiency: Operating margin of {operating_margin*100:.1f}%, above industry standards")
        
        # Signal 3: Financial Health
        current_ratio = get_ratio('Current_Ratio')
        debt_equity = get_ratio('Debt_to_Equity')
        if current_ratio and current_ratio > 1.5:
            bull_points.append(f"Solid liquidity: Current ratio of {current_ratio:.2f}, well-positioned to handle short-term obligations")
        elif debt_equity is not None and debt_equity < 0.5:
            bull_points.append(f"Conservative balance sheet: Debt-to-equity of {debt_equity:.2f}, providing financial flexibility")
        
        # Signal 4: Growth
        revenue_cagr = self.growth_rates.get('Total_Revenue_CAGR')
        if revenue_cagr and revenue_cagr > 0.10:  # Revenue CAGR > 10%
            bull_points.append(f"Consistent growth: {revenue_cagr*100:.1f}% revenue CAGR demonstrates strong market demand")
        
        # Signal 5: Cash Generation
        if not self.ratios.empty and 'Operating_Cash_Flow' in self.ratios.index:
            ocf = get_ratio('Operating_Cash_Flow')
            net_income = get_ratio('Net_Income')
            if ocf and net_income and ocf > net_income * 1.2:
                bull_points.append(f"Excellent cash generation: Operating cash flow exceeds net income, indicating high-quality earnings")
        
        # If we have < 3 points, add generic positive signals
        while len(bull_points) < 3:
            if len(bull_points) == 0:
                bull_points.append(f"Established market position with proven business model")
            elif len(bull_points) == 1:
                bull_points.append(f"Experienced management team with industry expertise")
            else:
                bull_points.append(f"Diversified revenue streams provide stability")
        
        # Return top 3 points
        return bull_points[:3]
    
    def generate_bear_case(self) -> List[str]:
        """
        Auto-generate bear case bullets from negative financial signals
        
        Returns:
            List of 3 bear case points
        """
        bear_points = []
        
        # Helper to get ratio value
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        # Signal 1: Valuation
        pe_ratio = get_ratio('PE_Ratio')
        if pe_ratio and pe_ratio > 30:  # P/E > 30
            bear_points.append(f"Premium valuation: P/E ratio of {pe_ratio:.1f}x may limit upside potential")
        elif pe_ratio and pe_ratio < 0:
            bear_points.append(f"Currently unprofitable: Negative earnings raise concerns about sustainability")
        
        # Signal 2: Leverage
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity and debt_equity > 1.5:
            bear_points.append(f"High leverage: Debt-to-equity of {debt_equity:.2f} increases financial risk")
        
        # Signal 3: Growth Slowdown
        revenue_cagr = self.growth_rates.get('Total_Revenue_CAGR')
        if revenue_cagr and revenue_cagr < 0.03:  # Revenue CAGR < 3%
            bear_points.append(f"Slowing growth: {revenue_cagr*100:.1f}% revenue CAGR suggests market maturation")
        
        # Signal 4: Margins
        operating_margin = get_ratio('Operating_Margin')
        if operating_margin and operating_margin < 0.05:
            bear_points.append(f"Thin margins: Operating margin of {operating_margin*100:.1f}% leaves little room for error")
        
        # Signal 5: Liquidity
        current_ratio = get_ratio('Current_Ratio')
        if current_ratio and current_ratio < 1.0:
            bear_points.append(f"Liquidity concerns: Current ratio of {current_ratio:.2f} may strain short-term obligations")
        
        # Signal 6: Negative ROE
        roe = get_ratio('ROE')
        if roe and roe < 0:
            bear_points.append(f"Negative return on equity indicates value destruction for shareholders")
        
        # If we have < 3 points, add moderate concerns
        while len(bear_points) < 3:
            if len(bear_points) == 0:
                bear_points.append(f"Market volatility and macroeconomic headwinds present downside risks")
            elif len(bear_points) == 1:
                bear_points.append(f"Competitive pressures may impact market share and pricing power")
            else:
                bear_points.append(f"Regulatory changes and industry disruption pose ongoing challenges")
        
        # Return top 3 points
        return bear_points[:3]
    
    # ==========================================
    # RISK ASSESSMENT
    # ==========================================
    
    def assess_risks(self) -> Dict[str, str]:
        """
        Assess various risk categories
        
        Returns:
            Dict with risk categories and levels (LOW/MODERATE/HIGH)
        """
        risks = {}
        
        # Helper to get ratio value
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        # Financial Health Risk
        current_ratio = get_ratio('Current_Ratio')
        debt_equity = get_ratio('Debt_to_Equity')
        
        if current_ratio and debt_equity is not None:
            if current_ratio > 1.5 and debt_equity < 0.5:
                risks['Financial Health'] = 'LOW'
            elif current_ratio > 1.0 and debt_equity < 1.0:
                risks['Financial Health'] = 'MODERATE'
            else:
                risks['Financial Health'] = 'HIGH'
        else:
            risks['Financial Health'] = 'N/A'
        
        # Valuation Risk
        pe_ratio = get_ratio('PE_Ratio')
        if pe_ratio:
            if pe_ratio <= 15:  # Changed from < 15 to <= 15
                risks['Valuation'] = 'LOW'
            elif pe_ratio < 30:
                risks['Valuation'] = 'MODERATE'
            else:
                risks['Valuation'] = 'HIGH'
        else:
            risks['Valuation'] = 'N/A'
        
        # Growth Risk
        revenue_cagr = self.growth_rates.get('Total_Revenue_CAGR')
        if revenue_cagr:
            if revenue_cagr > 0.10:
                risks['Growth'] = 'LOW'
            elif revenue_cagr > 0:
                risks['Growth'] = 'MODERATE'
            else:
                risks['Growth'] = 'HIGH'
        else:
            risks['Growth'] = 'N/A'
        
        # Liquidity Risk
        if current_ratio:
            if current_ratio > 2.0:
                risks['Liquidity'] = 'LOW'
            elif current_ratio > 1.0:
                risks['Liquidity'] = 'MODERATE'
            else:
                risks['Liquidity'] = 'HIGH'
        else:
            risks['Liquidity'] = 'N/A'
        
        # Profitability Risk
        roe = get_ratio('ROE')
        operating_margin = get_ratio('Operating_Margin')
        if roe and operating_margin:
            if roe > 0.15 and operating_margin > 0.15:
                risks['Profitability'] = 'LOW'
            elif roe > 0 and operating_margin > 0:
                risks['Profitability'] = 'MODERATE'
            else:
                risks['Profitability'] = 'HIGH'
        else:
            risks['Profitability'] = 'N/A'
        
        return risks
    
    # ==========================================
    # VALUATION RANGE
    # ==========================================
    
    def calculate_valuation_range(self) -> Dict[str, float]:
        """
        Calculate bear/base/bull valuation targets
        
        Returns:
            Dict with bear_case, base_case, bull_case prices
        """
        # Helper to get ratio value
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        current_price = get_ratio('Current_Price')
        
        if not current_price or current_price <= 0:
            # Return placeholder values that maintain ordering
            return {
                'bear_case': 80.0,
                'base_case': 100.0,
                'bull_case': 125.0,
                'bear_pct': -20.0,
                'bull_pct': 25.0
            }
        
        # Simple valuation range based on current price
        # Bear: -20% to -25%
        # Base: Current
        # Bull: +20% to +30%
        
        bear_case = current_price * 0.80  # 20% downside
        base_case = current_price
        bull_case = current_price * 1.25  # 25% upside
        
        return {
            'bear_case': bear_case,
            'base_case': base_case,
            'bull_case': bull_case,
            'bear_pct': -20.0,
            'bull_pct': 25.0
        }
    
    # ==========================================
    # RED FLAGS DETECTION
    # ==========================================
    
    def detect_red_flags(self) -> List[str]:
        """
        Detect potential red flags in financials
        
        Returns:
            List of red flag warnings
        """
        red_flags = []
        
        # Helper to get ratio value
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        # Red Flag 1: Negative earnings
        roe = get_ratio('ROE')
        if roe and roe < 0:
            red_flags.append("⚠ Negative return on equity")
        
        # Red Flag 2: High debt
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity and debt_equity > 2.0:
            red_flags.append("⚠ High leverage (Debt/Equity > 2.0)")
        
        # Red Flag 3: Liquidity crisis
        current_ratio = get_ratio('Current_Ratio')
        if current_ratio and current_ratio < 0.8:
            red_flags.append("⚠ Severe liquidity concerns (Current Ratio < 0.8)")
        
        # Red Flag 4: Declining revenues
        revenue_cagr = self.growth_rates.get('Total_Revenue_CAGR')
        if revenue_cagr and revenue_cagr < -0.05:  # Revenue declining > 5% CAGR
            red_flags.append("⚠ Revenue decline (negative growth)")
        
        # Red Flag 5: Extreme valuation
        pe_ratio = get_ratio('PE_Ratio')
        if pe_ratio and pe_ratio > 100:
            red_flags.append("⚠ Extreme valuation (P/E > 100x)")
        
        if len(red_flags) == 0:
            red_flags.append("✅ No major red flags detected")
        
        return red_flags


    # ==========================================
    # IC-READY ENHANCEMENTS
    # ==========================================
    
    def generate_recommendation(self) -> Dict:
        """
        Generate BUY/HOLD/SELL recommendation with conviction level
        
        Returns:
            Dict with recommendation, conviction, price_target, upside_pct
        """
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        # Get valuation metrics
        valuation = self.calculate_valuation_range()
        pe_ratio = get_ratio('PE_Ratio')
        roe = get_ratio('ROE')
        
        # Calculate upside to bull case
        current_price = valuation['base_case']
        bull_price = valuation['bull_case']
        bear_price = valuation['bear_case']
        
        upside_pct = ((bull_price - current_price) / current_price) * 100 if current_price > 0 else 0
        downside_pct = ((current_price - bear_price) / current_price) * 100 if current_price > 0 else 0
        
        # Price target: 70% weight to bull, 30% weight to base
        price_target = (bull_price * 0.7) + (current_price * 0.3)
        target_upside = ((price_target - current_price) / current_price) * 100 if current_price > 0 else 0
        
        # Recommendation logic
        recommendation = "HOLD"
        conviction = "MEDIUM"
        
        # BUY criteria: Upside > 15%, ROE > 10%, Risk/Reward > 1.5
        risk_reward = upside_pct / downside_pct if downside_pct > 0 else 0
        
        if target_upside > 20 and (roe is None or roe > 0.12) and risk_reward > 1.8:
            recommendation = "BUY"
            conviction = "HIGH"
        elif target_upside > 10 and (roe is None or roe > 0.08):
            recommendation = "BUY"
            conviction = "MEDIUM"
        elif target_upside < -10 or (roe and roe < 0):
            recommendation = "SELL"
            conviction = "MEDIUM"
        
        return {
            'recommendation': recommendation,
            'conviction': conviction,
            'price_target': price_target,
            'upside_pct': target_upside,
            'current_price': current_price,
            'risk_reward': risk_reward
        }
    
    def generate_investment_thesis(self) -> List[str]:
        """
        Generate 2-3 sentence investment thesis points
        
        Returns:
            List of thesis statements
        """
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        thesis_points = []
        
        # Point 1: Growth story
        revenue_cagr = get_ratio('Total_Revenue_CAGR')
        if revenue_cagr and revenue_cagr > 0.10:
            thesis_points.append(f"Strong revenue growth trajectory at {revenue_cagr*100:.0f}% CAGR positions company for market share expansion")
        elif revenue_cagr and revenue_cagr > 0:
            thesis_points.append(f"Stable revenue growth at {revenue_cagr*100:.0f}% CAGR provides predictable cash flow generation")
        else:
            thesis_points.append("Established market position with stable revenue base")
        
        # Point 2: Profitability/Returns
        roe = get_ratio('ROE')
        if roe and roe > 0.15:
            thesis_points.append(f"Superior capital efficiency with ROE of {roe*100:.1f}% demonstrates competitive moat")
        elif roe and roe > 0:
            thesis_points.append(f"Profitable operations with ROE of {roe*100:.1f}% provide shareholder value creation")
        else:
            thesis_points.append("Focus on operational improvement and margin expansion")
        
        # Point 3: Valuation/Risk
        pe_ratio = get_ratio('PE_Ratio')
        debt_equity = get_ratio('Debt_to_Equity')
        
        if pe_ratio and pe_ratio < 20 and (debt_equity is None or debt_equity < 1.0):
            thesis_points.append(f"Attractive valuation at {pe_ratio:.1f}x P/E with strong balance sheet provides downside protection")
        elif debt_equity and debt_equity < 0.5:
            thesis_points.append("Fortress balance sheet enables strategic flexibility and capital return opportunities")
        else:
            thesis_points.append("Valuation reflects current market conditions with room for multiple expansion")
        
        return thesis_points[:3]  # Return max 3 points
    
    def generate_why_now_catalyst(self) -> List[str]:
        """
        Generate "Why Now?" catalysts for timing the investment
        
        Returns:
            List of catalyst statements
        """
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        catalysts = []
        
        # Catalyst 1: Valuation opportunity
        pe_ratio = get_ratio('PE_Ratio')
        if pe_ratio and pe_ratio < 15:
            catalysts.append(f"Trading at {pe_ratio:.1f}x P/E, below historical average - potential mean reversion")
        elif pe_ratio and pe_ratio < 20:
            catalysts.append(f"Reasonable valuation at {pe_ratio:.1f}x P/E provides entry opportunity before re-rating")
        
        # Catalyst 2: Growth inflection
        revenue_cagr = get_ratio('Total_Revenue_CAGR')
        if revenue_cagr and revenue_cagr > 0.15:
            catalysts.append(f"Accelerating growth momentum ({revenue_cagr*100:.0f}% CAGR) not yet reflected in valuation")
        
        # Catalyst 3: Margin expansion
        operating_margin = get_ratio('Operating_Margin')
        if operating_margin and operating_margin > 0.15:
            catalysts.append(f"Operating leverage at {operating_margin*100:.1f}% margin drives earnings acceleration")
        
        # Catalyst 4: Balance sheet strength
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity is not None and debt_equity < 0.5:
            catalysts.append("Strong balance sheet enables M&A opportunities and increased capital returns")
        
        # Default catalysts if nothing specific
        if not catalysts:
            catalysts.append("Market dislocation creates tactical entry opportunity")
            catalysts.append("Quarterly earnings catalyst expected to drive positive sentiment")
        
        return catalysts[:3]  # Return max 3 catalysts
    
    def triage_red_flags(self) -> Dict:
        """
        Categorize red flags by severity: Deal-breaker, Monitor, Manageable
        
        Returns:
            Dict with 'deal_breaker', 'monitor', 'manageable' lists
        """
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        deal_breakers = []
        monitor = []
        manageable = []
        
        # Check critical issues
        roe = get_ratio('ROE')
        if roe and roe < -0.10:
            deal_breakers.append("Persistent negative ROE below -10% indicates fundamental business model issues")
        
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity and debt_equity > 5.0:
            deal_breakers.append(f"Extreme leverage at {debt_equity:.1f}x Debt/Equity poses solvency risk")
        elif debt_equity and debt_equity > 2.0:
            monitor.append(f"Elevated leverage at {debt_equity:.1f}x Debt/Equity requires monitoring of debt covenants")
        elif debt_equity and debt_equity > 1.0:
            manageable.append(f"Moderate leverage at {debt_equity:.1f}x Debt/Equity is within industry norms")
        
        # Liquidity issues
        current_ratio = get_ratio('Current_Ratio')
        if current_ratio and current_ratio < 0.8:
            monitor.append(f"Low liquidity at {current_ratio:.2f}x Current Ratio may stress working capital")
        elif current_ratio and current_ratio < 1.2:
            manageable.append(f"Adequate liquidity at {current_ratio:.2f}x Current Ratio covers near-term obligations")
        
        # Margin pressure
        operating_margin = get_ratio('Operating_Margin')
        if operating_margin and operating_margin < 0:
            monitor.append(f"Negative operating margin of {operating_margin*100:.1f}% indicates pricing or cost challenges")
        elif operating_margin and operating_margin < 0.05:
            manageable.append(f"Thin operating margin of {operating_margin*100:.1f}% leaves limited room for error")
        
        # Default messages if all clear
        if not deal_breakers and not monitor and not manageable:
            manageable.append("Standard business and market risks apply")
        
        return {
            'deal_breaker': deal_breakers if deal_breakers else ["None identified"],
            'monitor': monitor if monitor else ["No critical issues requiring immediate attention"],
            'manageable': manageable if manageable else ["Routine operational risks"]
        }
    
    def generate_peer_comparison(self) -> Dict:
        """
        Generate comparable company valuation data
        Note: This is a simplified version using sector averages
        In production, would fetch real peer data from API
        
        Returns:
            Dict with company and peer metrics
        """
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        # Get company metrics
        pe_ratio = get_ratio('PE_Ratio')
        price_to_book = get_ratio('Price_to_Book')
        roe = get_ratio('ROE')
        debt_equity = get_ratio('Debt_to_Equity')
        
        # Estimate sector averages (in production, fetch from API)
        # These are reasonable market averages for large-cap stocks
        sector_pe = 20.0
        sector_pb = 3.5
        sector_roe = 0.15
        sector_de = 1.2
        
        # Calculate premium/discount
        pe_premium = ((pe_ratio / sector_pe) - 1) * 100 if pe_ratio and sector_pe else None
        pb_premium = ((price_to_book / sector_pb) - 1) * 100 if price_to_book and sector_pb else None
        
        return {
            'company': {
                'PE': pe_ratio,
                'PB': price_to_book,
                'ROE': roe,
                'DE': debt_equity
            },
            'sector': {
                'PE': sector_pe,
                'PB': sector_pb,
                'ROE': sector_roe,
                'DE': sector_de
            },
            'premium': {
                'PE': pe_premium,
                'PB': pb_premium
            }
        }
    
    def generate_catalyst_timeline(self) -> List[Dict]:
        """
        Generate expected catalysts with timing and price impact
        
        Returns:
            List of catalyst dicts with quarter, event, impact
        """
        def get_ratio(key):
            if not self.ratios.empty and key in self.ratios.index:
                return self.ratios.loc[key].iloc[0]
            return None
        
        catalysts = []
        current_price = get_ratio('Current_Price') or 0
        
        # Catalyst 1: Earnings/Growth
        revenue_cagr = get_ratio('Total_Revenue_CAGR')
        if revenue_cagr and revenue_cagr > 0.10:
            catalysts.append({
                'quarter': 'Q1 2025',
                'event': f'Revenue growth acceleration ({revenue_cagr*100:.0f}% CAGR)',
                'impact': current_price * 0.04  # ~4% impact
            })
        elif revenue_cagr and revenue_cagr > 0:
            catalysts.append({
                'quarter': 'Q1 2025',
                'event': 'Quarterly earnings beat expectations',
                'impact': current_price * 0.03  # ~3% impact
            })
        
        # Catalyst 2: Margin expansion
        operating_margin = get_ratio('Operating_Margin')
        if operating_margin and operating_margin > 0.15:
            catalysts.append({
                'quarter': 'Q2 2025',
                'event': f'Operating leverage drives margin expansion',
                'impact': current_price * 0.03  # ~3% impact
            })
        else:
            catalysts.append({
                'quarter': 'Q2 2025',
                'event': 'Cost optimization initiatives',
                'impact': current_price * 0.02  # ~2% impact
            })
        
        # Catalyst 3: Capital allocation
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity is not None and debt_equity < 0.5:
            catalysts.append({
                'quarter': 'Q3 2025',
                'event': 'Share buyback or dividend increase',
                'impact': current_price * 0.03  # ~3% impact
            })
        else:
            catalysts.append({
                'quarter': 'Q3 2025',
                'event': 'Strategic M&A or partnership',
                'impact': current_price * 0.025  # ~2.5% impact
            })
        
        return catalysts[:3]  # Return max 3 catalysts


# ==========================================
# HELPER FUNCTIONS FOR PDF EXPORT
# ==========================================

def _calculate_health_score(financials: Dict) -> float:
    """Calculate overall financial health score 0-100 for PDF export."""
    import pandas as pd
    
    ratios = financials.get('ratios', pd.DataFrame())
    score = 50  # Base score
    
    def get_ratio_val(key):
        if not ratios.empty and key in ratios.index:
            val = ratios.loc[key].iloc[0]
            return val if pd.notnull(val) else None
        return None
    
    roe_val = get_ratio_val('ROE')
    if roe_val:
        if roe_val > 0.15: score += 20
        elif roe_val > 0.10: score += 10
        elif roe_val < 0: score -= 15
    
    debt_eq = get_ratio_val('Debt_to_Equity')
    if debt_eq:
        if debt_eq < 0.5: score += 15
        elif debt_eq < 1.0: score += 5
        elif debt_eq > 2.0: score -= 15
    
    curr_ratio = get_ratio_val('Current_Ratio')
    if curr_ratio:
        if curr_ratio > 2.0: score += 15
        elif curr_ratio > 1.5: score += 10
        elif curr_ratio < 1.0: score -= 15
    
    return max(0, min(100, score))


# ==========================================
# STREAMLIT RENDERING FUNCTION
# ==========================================

def render_investment_summary_tab(financials: Dict):
    """
    Render the Investment Summary tab in Streamlit
    
    Args:
        financials: Dictionary from USAFinancialExtractor
    """
    
    generator = InvestmentSummaryGenerator(financials)
    
    # Get recommendation
    recommendation_data = generator.generate_recommendation()
    rec = recommendation_data['recommendation']
    conviction = recommendation_data['conviction']
    price_target = recommendation_data['price_target']
    upside_pct = recommendation_data['upside_pct']
    
    # Color coding for recommendation
    if rec == "BUY":
        rec_color = '#4caf50'
        rec_bg = 'rgba(76, 175, 80, 0.15)'
        rec_icon = '🟢'
    elif rec == "SELL":
        rec_color = '#f44336'
        rec_bg = 'rgba(244, 67, 54, 0.15)'
        rec_icon = '🔴'
    else:  # HOLD
        rec_color = '#ff9800'
        rec_bg = 'rgba(255, 152, 0, 0.15)'
        rec_icon = '🟡'
    
    # Professional Header - IC Style
    st.markdown(f"""
    <div style='text-align: center; padding: 1.5rem 0; 
                border-bottom: 1px solid rgba(59, 130, 246, 0.15);'>
        <div style='display: inline-block; padding: 0.8rem 2rem; margin-bottom: 1rem;
                    background: {rec_bg}; border: 2px solid {rec_color};
                    border-radius: 8px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);'>
            <h2 style='color: {rec_color}; margin: 0; font-size: 1.6rem; font-weight: 700; letter-spacing: 1.5px;'>
                {rec_icon} {rec} | PT: ${price_target:.0f} | {upside_pct:+.0f}% | {conviction} CONVICTION
            </h2>
        </div>
        <div style='border-bottom: 1px solid rgba(59, 130, 246, 0.1); padding-bottom: 0.8rem; margin-bottom: 0.8rem;'>
            <h1 style='color: #3b82f6; font-size: 2.5rem; margin: 0.3rem 0; font-weight: 600;'>
                {generator.ticker}
            </h1>
            <p style='color: #94a3b8; font-size: 1rem; margin: 0; font-weight: 400;'>
                {generator.company_name}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Investment Score Gauges - Always show (with fallback if ECharts unavailable)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.3rem; margin: 1.5rem 0 1rem 0;
               letter-spacing: 1px;'>
        <i class="bi bi-speedometer2" style="margin-right: 0.5rem;"></i>SCORE DASHBOARD
    </h3>
    """, unsafe_allow_html=True)
    
    # Calculate conviction score (0-100)
    conviction_map = {'LOW': 33, 'MEDIUM': 66, 'HIGH': 100}
    conviction_score = conviction_map.get(conviction, 50)
    
    # Calculate health score from multiple metrics
    def calculate_health_score():
        """Calculate overall financial health score 0-100"""
        ratios = financials.get('ratios', pd.DataFrame())
        score = 50  # Base score
        
        def get_ratio(key):
            if not ratios.empty and key in ratios.index:
                val = ratios.loc[key].iloc[0]
                return val if pd.notnull(val) else None
            return None
        
        # ROE component (+/-20)
        roe = get_ratio('ROE')
        if roe:
            if roe > 0.15: score += 20
            elif roe > 0.10: score += 10
            elif roe < 0: score -= 15
        
        # Debt/Equity component (+/-15)
        debt_equity = get_ratio('Debt_to_Equity')
        if debt_equity:
            if debt_equity < 0.5: score += 15
            elif debt_equity < 1.0: score += 5
            elif debt_equity > 2.0: score -= 15
        
        # Current Ratio component (+/-15)
        current_ratio = get_ratio('Current_Ratio')
        if current_ratio:
            if current_ratio > 2.0: score += 15
            elif current_ratio > 1.5: score += 10
            elif current_ratio < 1.0: score -= 15
        
        return max(0, min(100, score))
    
    health_score = calculate_health_score()
    
    # Calculate risk score
    risk_reward = recommendation_data.get('risk_reward', 1.0)
    risk_score = min(100, max(0, risk_reward * 40))  # Scale to 0-100
    
    # Use ECharts gauges if available, otherwise use native metrics
    if UI_COMPONENTS_AVAILABLE and ECHARTS_AVAILABLE:
        gauge_cols = st.columns(3)
        
        with gauge_cols[0]:
            render_gauge(
                value=conviction_score,
                title="Conviction Level",
                min_value=0,
                max_value=100,
                thresholds=[(40, '#ef4444'), (70, '#f59e0b'), (100, '#10b981')],
                height=200,
                key="conviction_gauge"
            )
        
        with gauge_cols[1]:
            render_gauge(
                value=health_score,
                title="Financial Health",
                min_value=0,
                max_value=100,
                thresholds=[(40, '#ef4444'), (70, '#f59e0b'), (100, '#10b981')],
                height=200,
                key="health_gauge"
            )
        
        with gauge_cols[2]:
            render_gauge(
                value=risk_score,
                title="Risk/Reward",
                min_value=0,
                max_value=100,
                thresholds=[(30, '#ef4444'), (60, '#f59e0b'), (100, '#10b981')],
                height=200,
                key="risk_gauge"
            )
    else:
        # Fallback: Native Streamlit metrics with progress bars
        gauge_cols = st.columns(3)
        
        def get_score_color(score):
            if score < 40: return "🔴"
            elif score < 70: return "🟡"
            else: return "🟢"
        
        with gauge_cols[0]:
            st.metric("Conviction Level", f"{get_score_color(conviction_score)} {conviction_score}/100")
            st.progress(conviction_score / 100)
        
        with gauge_cols[1]:
            st.metric("Financial Health", f"{get_score_color(health_score)} {health_score}/100")
            st.progress(health_score / 100)
        
        with gauge_cols[2]:
            st.metric("Risk/Reward", f"{get_score_color(risk_score)} {risk_score:.0f}/100")
            st.progress(risk_score / 100)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Business Model Section
    info = financials.get('info', {})
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    employees = info.get('fullTimeEmployees', 'N/A')
    website = info.get('website', 'N/A')
    business_summary = info.get('longBusinessSummary', 'No business description available')
    
    st.markdown("""
    <h3 style='color: #3b82f6; font-weight: 700; font-size: 1.3rem; margin: 1.5rem 0 1rem 0;
               letter-spacing: 1px;'>
        <i class="bi bi-building" style="margin-right: 0.5rem;"></i>BUSINESS MODEL
    </h3>
    """, unsafe_allow_html=True)
    
    # Business metrics in compact card format
    biz_col1, biz_col2, biz_col3, biz_col4 = st.columns(4)
    
    with biz_col1:
        st.markdown(f"""
        <div style='padding: 0.8rem; background: rgba(59, 130, 246, 0.08); border-radius: 6px; text-align: center;'>
            <p style='color: #3b82f6; font-size: 0.75rem; margin: 0; font-weight: 600;'>SECTOR</p>
            <p style='color: #f0f4f8; font-size: 0.9rem; margin: 0.3rem 0 0 0; font-weight: 600;'>{sector}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with biz_col2:
        st.markdown(f"""
        <div style='padding: 0.8rem; background: rgba(59, 130, 246, 0.08); border-radius: 6px; text-align: center;'>
            <p style='color: #3b82f6; font-size: 0.75rem; margin: 0; font-weight: 600;'>INDUSTRY</p>
            <p style='color: #f0f4f8; font-size: 0.9rem; margin: 0.3rem 0 0 0; font-weight: 600;'>{industry}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with biz_col3:
        st.markdown(f"""
        <div style='padding: 0.8rem; background: rgba(59, 130, 246, 0.08); border-radius: 6px; text-align: center;'>
            <p style='color: #3b82f6; font-size: 0.75rem; margin: 0; font-weight: 600;'>EMPLOYEES</p>
            <p style='color: #f0f4f8; font-size: 0.9rem; margin: 0.3rem 0 0 0; font-weight: 600;'>{f'{employees:,}' if isinstance(employees, int) else employees}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with biz_col4:
        if website and website != 'N/A':
            st.markdown(f"""
            <div style='padding: 0.8rem; background: rgba(59, 130, 246, 0.08); border-radius: 6px; text-align: center;'>
                <p style='color: #3b82f6; font-size: 0.75rem; margin: 0; font-weight: 600;'>WEBSITE</p>
                <a href='{website}' target='_blank' style='color: #10b981; font-size: 0.9rem; margin: 0.3rem 0 0 0; font-weight: 600; text-decoration: none;'>Visit →</a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='padding: 0.8rem; background: rgba(59, 130, 246, 0.08); border-radius: 6px; text-align: center;'>
                <p style='color: #3b82f6; font-size: 0.75rem; margin: 0; font-weight: 600;'>WEBSITE</p>
                <p style='color: white; font-size: 0.9rem; margin: 0.3rem 0 0 0; font-weight: 600;'>N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Business description - adaptive with expand/collapse
    if business_summary and business_summary != 'No business description available':
        # Determine if we need to truncate
        char_limit = 400
        is_long = len(business_summary) > char_limit
        
        if is_long:
            # Show truncated version with expander for full text
            short_summary = business_summary[:char_limit].rsplit(' ', 1)[0] + '...'
            
            st.markdown(f"""
            <div style='padding: 1rem; margin: 1rem 0;
                        background: rgba(59, 130, 246, 0.05);
                        border-left: 3px solid #1e88e5; border-radius: 4px;'>
                <p style='color: #e3f2fd; margin: 0; line-height: 1.6; font-size: 0.9rem;'>
                    {short_summary}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📖 Read Full Business Description", expanded=False):
                st.markdown(f"""
                <div style='padding: 1rem; background: rgba(59, 130, 246, 0.03);
                            border-radius: 6px; line-height: 1.7;'>
                    <p style='color: #e3f2fd; margin: 0; font-size: 0.9rem;'>
                        {business_summary}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Short enough to show fully
            st.markdown(f"""
            <div style='padding: 1rem; margin: 1rem 0;
                        background: rgba(59, 130, 246, 0.05);
                        border-left: 3px solid #1e88e5; border-radius: 4px;'>
                <p style='color: #e3f2fd; margin: 0; line-height: 1.6; font-size: 0.9rem;'>
                    {business_summary}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Investment Thesis Section
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.3rem; margin: 1.5rem 0 1rem 0;
               letter-spacing: 1px;'>
        <i class="bi bi-lightbulb-fill" style="margin-right: 0.5rem;"></i>INVESTMENT THESIS
    </h3>
    """, unsafe_allow_html=True)
    
    thesis_points = generator.generate_investment_thesis()
    for point in thesis_points:
        st.markdown(f"""
        <div style='padding: 0.8rem 1rem; margin-bottom: 0.5rem;
                    background: rgba(59, 130, 246, 0.08);
                    border-left: 3px solid #1e88e5; border-radius: 4px;'>
            <p style='color: #e3f2fd; margin: 0; line-height: 1.6; font-size: 0.95rem;'>
                {point}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Why Now? Catalyst Section
    st.markdown("""
    <h3 style='color: #ffd700; font-weight: 700; font-size: 1.3rem; margin: 1.5rem 0 1rem 0;
               letter-spacing: 1px;'>
        <i class="bi bi-clock-fill" style="margin-right: 0.5rem;"></i>WHY NOW?
    </h3>
    """, unsafe_allow_html=True)
    
    catalysts = generator.generate_why_now_catalyst()
    catalyst_cols = st.columns(len(catalysts))
    for idx, catalyst in enumerate(catalysts):
        with catalyst_cols[idx]:
            st.markdown(f"""
            <div style='text-align: center; padding: 1.2rem 0.8rem;
                        background: rgba(255, 215, 0, 0.08);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(255, 215, 0, 0.2);
                        border-radius: 8px; height: 100%;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);'>
                <p style='color: #e3f2fd; margin: 0; font-size: 0.9rem; line-height: 1.5;'>
                    {catalyst}
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Layout: Two columns for Bull/Bear
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.02);
                    backdrop-filter: blur(10px);
                    padding: 1.5rem; border-radius: 10px; 
                    border: 1px solid rgba(100, 181, 246, 0.15);
                    border-left: 3px solid #4caf50; height: 100%;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);'>
            <h3 style='color: #66bb6a; margin: 0 0 1rem 0; font-weight: 700; font-size: 1.2rem;
                       display: flex; align-items: center; letter-spacing: 1px;'>
                <span style='font-size: 1.5rem; margin-right: 0.5rem;'>▲</span> BULL CASE
            </h3>
        """, unsafe_allow_html=True)
        
        bull_case = generator.generate_bull_case()
        for i, point in enumerate(bull_case, 1):
            st.markdown(f"""
            <div style='margin-bottom: 0.8rem; padding-left: 0.5rem; border-left: 2px solid rgba(102, 187, 106, 0.4);'>
                <span style='color: #66bb6a; font-weight: 600;'>{i}.</span> 
                <span style='color: #e3f2fd;'>{point}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.02);
                    backdrop-filter: blur(10px);
                    padding: 1.5rem; border-radius: 10px; 
                    border: 1px solid rgba(100, 181, 246, 0.15);
                    border-left: 3px solid #f44336; height: 100%;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);'>
            <h3 style='color: #ef5350; margin: 0 0 1rem 0; font-weight: 700; font-size: 1.2rem;
                       display: flex; align-items: center; letter-spacing: 1px;'>
                <span style='font-size: 1.5rem; margin-right: 0.5rem;'>▼</span> BEAR CASE
            </h3>
        """, unsafe_allow_html=True)
        
        bear_case = generator.generate_bear_case()
        for i, point in enumerate(bear_case, 1):
            st.markdown(f"""
            <div style='margin-bottom: 0.8rem; padding-left: 0.5rem; border-left: 2px solid rgba(239, 83, 80, 0.4);'>
                <span style='color: #ef5350; font-weight: 600;'>{i}.</span> 
                <span style='color: #e3f2fd;'>{point}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Metrics Dashboard
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(59, 130, 246, 0.25); padding-bottom: 0.5rem;'>
        <i class="bi bi-graph-up" style="margin-right: 0.5rem;"></i>KEY METRICS
    </h3>
    """, unsafe_allow_html=True)
    
    # Helper to get ratio value - checks multiple sources
    def get_ratio(key):
        # First check ratios DataFrame
        if not generator.ratios.empty and key in generator.ratios.index:
            val = generator.ratios.loc[key].iloc[0]
            if val is not None and (not isinstance(val, float) or not pd.isna(val)):
                return val
        return None
    
    # Helper to get from info dict (yfinance direct data)
    info = financials.get('info', {})
    growth_rates = financials.get('growth_rates', {})
    
    # Get enhanced metrics - with fallback to info dict
    current_price = get_ratio('Current_Price') or info.get('currentPrice') or info.get('regularMarketPrice')
    pe_ratio = get_ratio('PE_Ratio') or info.get('trailingPE') or info.get('forwardPE')
    
    # Market Cap - try multiple sources
    market_cap = get_ratio('Market_Cap')
    if not market_cap:
        market_cap = info.get('marketCap')
    
    # Revenue - try multiple sources
    revenue = get_ratio('Revenue') or info.get('totalRevenue')
    
    # Net Income
    net_income = get_ratio('Net_Income') or info.get('netIncomeToCommon')
    
    # ROE - try ratio first, then info
    roe = get_ratio('ROE')
    if not roe:
        roe_info = info.get('returnOnEquity')
        if roe_info:
            roe = roe_info  # Already in decimal form from yfinance
    
    debt_equity = get_ratio('Debt_to_Equity') or info.get('debtToEquity')
    # yfinance returns D/E as percentage (e.g., 155 for 1.55x), convert if needed
    if debt_equity and debt_equity > 10:
        debt_equity = debt_equity / 100
    
    # Calculate FCF Yield (if data available) - with fallback
    operating_cash_flow = get_ratio('Operating_Cash_Flow') or info.get('operatingCashflow')
    capex = get_ratio('Capital_Expenditures') or info.get('capitalExpenditures')
    free_cash_flow = info.get('freeCashflow')
    
    if free_cash_flow and market_cap and market_cap > 0:
        fcf_yield = (free_cash_flow / market_cap) * 100
    elif operating_cash_flow and capex and market_cap and market_cap > 0:
        fcf = operating_cash_flow + capex  # capex is negative
        fcf_yield = (fcf / market_cap) * 100
    else:
        fcf_yield = None
    
    # Get ROIC (if available - use returnOnCapital from yfinance, fallback to ROE)
    roic = info.get('returnOnCapital') or info.get('returnOnAssets') or roe
    
    # Get Revenue CAGR - check growth_rates dict first
    revenue_cagr = None
    if growth_rates:
        # Try different keys for revenue CAGR
        revenue_cagr = growth_rates.get('Total_Revenue_CAGR')
        if revenue_cagr is None:
            revenue_cagr = growth_rates.get('Revenue_CAGR')
        # Convert from percentage if needed (e.g., 15.5 -> 0.155)
        if revenue_cagr is not None and abs(revenue_cagr) > 1:
            revenue_cagr = revenue_cagr / 100
    
    # Fallback to revenueGrowth from info (YoY growth as proxy)
    if revenue_cagr is None:
        revenue_cagr = info.get('revenueGrowth')
    
    # Get Debt/EBITDA
    ebitda = get_ratio('EBITDA')
    total_debt = get_ratio('Total_Debt')
    if ebitda and total_debt and ebitda > 0:
        debt_to_ebitda = total_debt / ebitda
    else:
        debt_to_ebitda = None
    
    # Display IC-READY metrics in professional layout
    st.markdown("""
    <div style='background: rgba(59, 130, 246, 0.05); padding: 1.5rem; border-radius: 10px;
                border: 1px solid rgba(59, 130, 246, 0.15); margin-bottom: 1.5rem;'>
    """, unsafe_allow_html=True)
    
    # Row 1: Valuation & Size
    metric_cols1 = st.columns(5)
    with metric_cols1[0]:
        st.metric("Current Price", f"${current_price:.2f}" if current_price else "N/A")
    with metric_cols1[1]:
        st.metric("P/E Ratio", f"{pe_ratio:.1f}x" if pe_ratio else "N/A")
    with metric_cols1[2]:
        if market_cap:
            st.metric("Market Cap", f"${market_cap/1e9:.1f}B")
        else:
            st.metric("Market Cap", "N/A")
    with metric_cols1[3]:
        if revenue:
            st.metric("Revenue (TTM)", f"${revenue/1e9:.1f}B")
        else:
            st.metric("Revenue", "N/A")
    with metric_cols1[4]:
        if revenue_cagr is not None:
            st.metric("Revenue CAGR", f"{revenue_cagr*100:.1f}%", 
                     delta=f"{'Growth' if revenue_cagr > 0 else 'Decline'}")
        else:
            st.metric("Revenue CAGR", "N/A")
    
    # Row 2: Profitability & Returns (IC FOCUS)
    metric_cols2 = st.columns(5)
    with metric_cols2[0]:
        if net_income:
            st.metric("Net Income", f"${net_income/1e9:.1f}B")
        else:
            st.metric("Net Income", "N/A")
    with metric_cols2[1]:
        if roe:
            st.metric("ROE", f"{roe*100:.1f}%", 
                     delta=f"{'Strong' if roe > 0.15 else 'Adequate' if roe > 0 else 'Negative'}")
        else:
            st.metric("ROE", "N/A")
    with metric_cols2[2]:
        if roic:
            st.metric("ROIC", f"{roic*100:.1f}%", 
                     delta=f"{'Above WACC' if roic > 0.10 else 'Below WACC'}")
        else:
            st.metric("ROIC", "N/A")
    with metric_cols2[3]:
        if fcf_yield:
            st.metric("FCF Yield", f"{fcf_yield:.1f}%", 
                     delta=f"{'Attractive' if fcf_yield > 5 else 'Fair' if fcf_yield > 3 else 'Low'}")
        else:
            st.metric("FCF Yield", "N/A")
    with metric_cols2[4]:
        if debt_to_ebitda:
            st.metric("Debt/EBITDA", f"{debt_to_ebitda:.1f}x", 
                     delta=f"{'High' if debt_to_ebitda > 3 else 'Moderate' if debt_to_ebitda > 1 else 'Low'}")
        elif debt_equity is not None:
            st.metric("Debt/Equity", f"{debt_equity:.2f}x")
        else:
            st.metric("Leverage", "N/A")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Add IC-style annotation
    st.markdown("""
    <div style='padding: 0.8rem; background: rgba(255, 215, 0, 0.08);
                border-left: 3px solid #ffd700; border-radius: 4px; margin-bottom: 1rem;'>
        <p style='color: #e3f2fd; margin: 0; font-size: 0.85rem; font-weight: 500;'>
            <strong style='color: #ffd700;'>IC Note:</strong> ROIC <span style='color: #66bb6a;'>>10%</span> indicates value creation. 
            FCF Yield <span style='color: #66bb6a;'>>5%</span> suggests strong cash generation. 
            Revenue CAGR <span style='color: #66bb6a;'>>10%</span> indicates growth momentum.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # COMPARABLE VALUATION (IC-Ready)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(59, 130, 246, 0.25); padding-bottom: 0.5rem;'>
        <i class="bi bi-bar-chart-fill" style="margin-right: 0.5rem;"></i>COMPARABLE VALUATION
    </h3>
    """, unsafe_allow_html=True)
    
    peer_data = generator.generate_peer_comparison()
    comp = peer_data['company']
    sector = peer_data['sector']
    premium = peer_data['premium']
    
    # Create comparison table
    st.markdown("""
    <div style='background: rgba(59, 130, 246, 0.05); padding: 1.5rem; border-radius: 10px;
                border: 1px solid rgba(59, 130, 246, 0.15);'>
    """, unsafe_allow_html=True)
    
    comp_cols = st.columns([2, 1, 1, 1, 1])
    
    # Header row
    with comp_cols[0]:
        st.markdown("<p style='color: #3b82f6; font-weight: 700; font-size: 0.9rem;'>Company</p>", unsafe_allow_html=True)
    with comp_cols[1]:
        st.markdown("<p style='color: #3b82f6; font-weight: 700; font-size: 0.9rem;'>P/E</p>", unsafe_allow_html=True)
    with comp_cols[2]:
        st.markdown("<p style='color: #3b82f6; font-weight: 700; font-size: 0.9rem;'>P/B</p>", unsafe_allow_html=True)
    with comp_cols[3]:
        st.markdown("<p style='color: #3b82f6; font-weight: 700; font-size: 0.9rem;'>ROE</p>", unsafe_allow_html=True)
    with comp_cols[4]:
        st.markdown("<p style='color: #3b82f6; font-weight: 700; font-size: 0.9rem;'>D/E</p>", unsafe_allow_html=True)
    
    # Company row
    comp_cols2 = st.columns([2, 1, 1, 1, 1])
    with comp_cols2[0]:
        st.markdown(f"<p style='color: white; font-weight: 600;'>{generator.ticker} (Company)</p>", unsafe_allow_html=True)
    with comp_cols2[1]:
        pe_val = f"{comp['PE']:.1f}x" if comp['PE'] else "N/A"
        st.markdown(f"<p style='color: #e3f2fd;'>{pe_val}</p>", unsafe_allow_html=True)
    with comp_cols2[2]:
        pb_val = f"{comp['PB']:.1f}x" if comp['PB'] else "N/A"
        st.markdown(f"<p style='color: #e3f2fd;'>{pb_val}</p>", unsafe_allow_html=True)
    with comp_cols2[3]:
        roe_val = f"{comp['ROE']*100:.1f}%" if comp['ROE'] else "N/A"
        st.markdown(f"<p style='color: #e3f2fd;'>{roe_val}</p>", unsafe_allow_html=True)
    with comp_cols2[4]:
        de_val = f"{comp['DE']:.2f}x" if comp['DE'] is not None else "N/A"
        st.markdown(f"<p style='color: #e3f2fd;'>{de_val}</p>", unsafe_allow_html=True)
    
    # Sector row
    comp_cols3 = st.columns([2, 1, 1, 1, 1])
    with comp_cols3[0]:
        st.markdown("<p style='color: #94a3b8;'>Sector Median</p>", unsafe_allow_html=True)
    with comp_cols3[1]:
        st.markdown(f"<p style='color: #94a3b8;'>{sector['PE']:.1f}x</p>", unsafe_allow_html=True)
    with comp_cols3[2]:
        st.markdown(f"<p style='color: #94a3b8;'>{sector['PB']:.1f}x</p>", unsafe_allow_html=True)
    with comp_cols3[3]:
        st.markdown(f"<p style='color: #94a3b8;'>{sector['ROE']*100:.1f}%</p>", unsafe_allow_html=True)
    with comp_cols3[4]:
        st.markdown(f"<p style='color: #94a3b8;'>{sector['DE']:.2f}x</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Premium/Discount analysis
    if premium['PE']:
        pe_status = "premium" if premium['PE'] > 0 else "discount"
        pe_color = "#66bb6a" if premium['PE'] > 0 else "#ef5350"
        st.markdown(f"""
        <div style='padding: 1rem; margin-top: 1rem; background: rgba(59, 130, 246, 0.08);
                    border-left: 3px solid #1e88e5; border-radius: 4px;'>
            <p style='color: #e3f2fd; margin: 0; font-size: 0.9rem; line-height: 1.6;'>
                <strong style='color: #42a5f5;'>Valuation Analysis:</strong> 
                Trading at <span style='color: {pe_color}; font-weight: 600;'>{abs(premium['PE']):.0f}% {pe_status}</span> to sector P/E.
                {f"Premium justified by superior ROE of {comp['ROE']*100:.1f}% vs. sector {sector['ROE']*100:.1f}%." if comp['ROE'] and comp['ROE'] > sector['ROE'] else ""}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CATALYST TIMELINE
    st.markdown("""
    <h3 style='color: #ffd700; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(255, 215, 0, 0.3); padding-bottom: 0.5rem;'>
        <i class="bi bi-calendar-event-fill" style="margin-right: 0.5rem;"></i>CATALYST TIMELINE
    </h3>
    """, unsafe_allow_html=True)
    
    catalysts = generator.generate_catalyst_timeline()
    
    # Visual timeline
    st.markdown("""
    <div style='background: rgba(255, 215, 0, 0.05); padding: 1.5rem; border-radius: 10px;
                border: 1px solid rgba(255, 215, 0, 0.2);'>
    """, unsafe_allow_html=True)
    
    total_impact = sum([c['impact'] for c in catalysts])
    current = get_ratio('Current_Price') or 0
    # Use official price target from recommendation (CONSISTENCY FIX)
    target = recommendation_data['price_target'] if recommendation_data else current + total_impact
    
    for idx, catalyst in enumerate(catalysts, 1):
        st.markdown(f"""
        <div style='margin-bottom: 1rem; padding: 1rem; background: rgba(255, 255, 255, 0.02);
                    border-left: 3px solid #ffd700; border-radius: 6px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div style='flex: 1;'>
                    <p style='color: #ffd700; margin: 0 0 0.3rem 0; font-weight: 700; font-size: 0.85rem;'>
                        {catalyst['quarter']}
                    </p>
                    <p style='color: #e3f2fd; margin: 0; font-size: 0.9rem;'>
                        {catalyst['event']}
                    </p>
                </div>
                <div style='text-align: right; min-width: 80px;'>
                    <p style='color: #66bb6a; margin: 0; font-weight: 700; font-size: 1.1rem;'>
                        +${catalyst['impact']:.0f}
                    </p>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.75rem;'>
                        impact
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Summary bar
    if current > 0 and target > 0:
        st.markdown(f"""
        <div style='margin-top: 1.5rem; padding: 1.5rem; background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(255, 215, 0, 0.1) 100%);
                    border: 2px solid #ffd700; border-radius: 8px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <div>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Current Price</p>
                    <p style='color: white; margin: 0; font-weight: 700; font-size: 1.5rem;'>${current:.0f}</p>
                </div>
                <div style='text-align: center;'>
                    <p style='color: #ffd700; margin: 0; font-size: 1.2rem;'>→ +${total_impact:.0f} →</p>
                </div>
                <div style='text-align: right;'>
                    <p style='color: #94a3b8; margin: 0; font-size: 0.85rem;'>Target Price</p>
                    <p style='color: #66bb6a; margin: 0; font-weight: 700; font-size: 1.5rem;'>${target:.0f}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Risk Assessment
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(59, 130, 246, 0.25); padding-bottom: 0.5rem;'>
        <i class="bi bi-exclamation-triangle-fill" style="margin-right: 0.5rem;"></i>RISK ASSESSMENT
    </h3>
    """, unsafe_allow_html=True)
    
    risks = generator.assess_risks()
    risk_cols = st.columns(len(risks))
    
    for idx, (risk_category, risk_level) in enumerate(risks.items()):
        with risk_cols[idx]:
            # Color coding with glassmorphism
            if risk_level == 'LOW':
                border_color = '#4caf50'
                text_color = '#66bb6a'
                icon = '●'
            elif risk_level == 'MODERATE':
                border_color = '#ff9800'
                text_color = '#ffb74d'
                icon = '●'
            elif risk_level == 'HIGH':
                border_color = '#f44336'
                text_color = '#ef5350'
                icon = '●'
            else:
                border_color = '#9e9e9e'
                text_color = '#bdbdbd'
                icon = '○'
            
            st.markdown(f"""
            <div style='text-align: center; padding: 1.5rem 1rem; 
                        background: rgba(255, 255, 255, 0.02);
                        backdrop-filter: blur(10px);
                        border: 1px solid rgba(100, 181, 246, 0.15);
                        border-left: 3px solid {border_color};
                        border-radius: 10px;
                        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);'>
                <div style='font-size: 2.5rem; color: {text_color}; margin-bottom: 0.5rem;'>{icon}</div>
                <div style='font-weight: 600; margin: 0.5rem 0; color: #e3f2fd; font-size: 0.85rem; 
                           text-transform: uppercase; letter-spacing: 1px;'>{risk_category}</div>
                <div style='color: {text_color}; font-size: 1.3rem; font-weight: 700;'>{risk_level}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Valuation Range
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(59, 130, 246, 0.25); padding-bottom: 0.5rem;'>
        <i class="bi bi-cash-stack" style="margin-right: 0.5rem;"></i>VALUATION RANGE
    </h3>
    """, unsafe_allow_html=True)
    
    valuation = generator.calculate_valuation_range()
    
    val_cols = st.columns(3)
    
    with val_cols[0]:
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem 1rem; 
                    background: rgba(255, 255, 255, 0.02);
                    backdrop-filter: blur(10px);
                    border-radius: 10px; border: 1px solid rgba(100, 181, 246, 0.15);
                    border-left: 3px solid #f44336;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);'>
            <div style='color: #ef5350; font-weight: 700; font-size: 0.8rem; letter-spacing: 1.5px; text-transform: uppercase;'>BEAR CASE</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 1rem 0; color: white;'>${valuation['bear_case']:.2f}</div>
            <div style='color: #ef5350; font-size: 1rem; font-weight: 600;'>{valuation['bear_pct']:.0f}% downside</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_cols[1]:
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem 1rem; 
                    background: rgba(255, 255, 255, 0.03);
                    backdrop-filter: blur(10px);
                    border-radius: 10px; border: 1px solid rgba(100, 181, 246, 0.25);
                    border-left: 4px solid #1e88e5;
                    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.12);'>
            <div style='color: #42a5f5; font-weight: 700; font-size: 0.8rem; letter-spacing: 1.5px; text-transform: uppercase;'>BASE CASE</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 1rem 0; color: white;'>${valuation['base_case']:.2f}</div>
            <div style='color: #3b82f6; font-size: 1rem; font-weight: 600;'>Current Price</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_cols[2]:
        st.markdown(f"""
        <div style='text-align: center; padding: 2rem 1rem; 
                    background: rgba(255, 255, 255, 0.02);
                    backdrop-filter: blur(10px);
                    border-radius: 10px; border: 1px solid rgba(100, 181, 246, 0.15);
                    border-left: 3px solid #4caf50;
                    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);'>
            <div style='color: #66bb6a; font-weight: 700; font-size: 0.8rem; letter-spacing: 1.5px; text-transform: uppercase;'>BULL CASE</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 1rem 0; color: white;'>${valuation['bull_case']:.2f}</div>
            <div style='color: #66bb6a; font-size: 1rem; font-weight: 600;'>+{valuation['bull_pct']:.0f}% upside</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Risk Severity Matrix (IC-Ready)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(59, 130, 246, 0.25); padding-bottom: 0.5rem;'>
        <i class="bi bi-shield-fill-exclamation" style="margin-right: 0.5rem;"></i>RISK SEVERITY MATRIX
    </h3>
    """, unsafe_allow_html=True)
    
    risk_triage = generator.triage_red_flags()
    
    # Deal-Breakers (RED)
    st.markdown("""
    <div style='padding: 0.5rem 1rem; margin-bottom: 0.8rem;
                background: rgba(244, 67, 54, 0.1);
                border-left: 4px solid #f44336; border-radius: 6px;'>
        <h4 style='color: #ef5350; margin: 0.3rem 0; font-size: 1rem; font-weight: 700; letter-spacing: 0.5px;'>
            🔴 DEAL-BREAKER
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    for flag in risk_triage['deal_breaker']:
        st.markdown(f"""
        <div style='padding: 0.8rem 1rem; margin: 0.3rem 0 0.3rem 1.5rem;
                    background: rgba(255, 255, 255, 0.02);
                    border-left: 2px solid rgba(239, 83, 80, 0.4);
                    border-radius: 4px;'>
            <p style='color: #ef5350; margin: 0; font-size: 0.9rem;'>{flag}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Monitor (YELLOW)
    st.markdown("""
    <div style='padding: 0.5rem 1rem; margin: 0.8rem 0 0.8rem 0;
                background: rgba(255, 152, 0, 0.1);
                border-left: 4px solid #ff9800; border-radius: 6px;'>
        <h4 style='color: #ffb74d; margin: 0.3rem 0; font-size: 1rem; font-weight: 700; letter-spacing: 0.5px;'>
            🟡 MONITOR
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    for flag in risk_triage['monitor']:
        st.markdown(f"""
        <div style='padding: 0.8rem 1rem; margin: 0.3rem 0 0.3rem 1.5rem;
                    background: rgba(255, 255, 255, 0.02);
                    border-left: 2px solid rgba(255, 183, 77, 0.4);
                    border-radius: 4px;'>
            <p style='color: #e3f2fd; margin: 0; font-size: 0.9rem;'>{flag}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Manageable (GREEN)
    st.markdown("""
    <div style='padding: 0.5rem 1rem; margin: 0.8rem 0 0.8rem 0;
                background: rgba(76, 175, 80, 0.1);
                border-left: 4px solid #4caf50; border-radius: 6px;'>
        <h4 style='color: #66bb6a; margin: 0.3rem 0; font-size: 1rem; font-weight: 700; letter-spacing: 0.5px;'>
            🟢 MANAGEABLE
        </h4>
    </div>
    """, unsafe_allow_html=True)
    
    for flag in risk_triage['manageable']:
        st.markdown(f"""
        <div style='padding: 0.8rem 1rem; margin: 0.3rem 0 0.3rem 1.5rem;
                    background: rgba(255, 255, 255, 0.02);
                    border-left: 2px solid rgba(102, 187, 106, 0.4);
                    border-radius: 4px;'>
            <p style='color: #66bb6a; margin: 0; font-size: 0.9rem;'>{flag}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # THE ASK - Action-Oriented Recommendation
    st.markdown("""
    <h3 style='color: #ffd700; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(255, 215, 0, 0.3); padding-bottom: 0.5rem;'>
        <i class="bi bi-bullseye" style="margin-right: 0.5rem;"></i>THE ASK
    </h3>
    """, unsafe_allow_html=True)
    
    # Generate action items based on recommendation
    rec_data = recommendation_data
    current_price = rec_data['current_price']
    target_price = rec_data['price_target']
    risk_reward = rec_data['risk_reward']
    
    valuation = generator.calculate_valuation_range()
    bear_price = valuation['bear_case']
    
    if rec == "BUY":
        action_bg = 'rgba(76, 175, 80, 0.15)'
        action_border = '#4caf50'
        action_text = f"""<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #66bb6a;'>Recommendation:</strong> Initiate position at current levels (${current_price:.0f})
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #66bb6a;'>Price Target (12M):</strong> ${target_price:.0f} ({rec_data['upside_pct']:+.0f}% upside potential)
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #66bb6a;'>Entry Strategy:</strong> Build position over 2-3 weeks. Add on dips below ${current_price * 0.95:.0f}
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #66bb6a;'>Stop-Loss:</strong> ${bear_price * 1.05:.0f} (protect capital if thesis breaks)
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #66bb6a;'>Risk/Reward:</strong> {risk_reward:.1f}:1 (favorable asymmetry)
</p>"""
    elif rec == "SELL":
        action_bg = 'rgba(244, 67, 54, 0.15)'
        action_border = '#f44336'
        action_text = f"""<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ef5350;'>Recommendation:</strong> Exit position or avoid initiation at current levels
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ef5350;'>Price Target (12M):</strong> ${target_price:.0f} ({rec_data['upside_pct']:+.0f}% downside risk)
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ef5350;'>Action:</strong> Liquidate holdings and redeploy capital to higher-conviction opportunities
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ef5350;'>Re-entry Point:</strong> Consider revisiting below ${bear_price:.0f} if fundamentals improve
</p>"""
    else:  # HOLD
        action_bg = 'rgba(255, 152, 0, 0.15)'
        action_border = '#ff9800'
        action_text = f"""<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ffb74d;'>Recommendation:</strong> Maintain current position, do not add or trim
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ffb74d;'>Price Target (12M):</strong> ${target_price:.0f} ({rec_data['upside_pct']:+.0f}% expected return)
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ffb74d;'>Action:</strong> Monitor quarterly earnings and wait for better entry point
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ffb74d;'>Add Signal:</strong> Below ${current_price * 0.90:.0f} (10% pullback)
</p>
<p style='color: #e3f2fd; margin: 0.8rem 0; line-height: 1.8; font-size: 1rem;'>
<strong style='color: #ffb74d;'>Trim Signal:</strong> Above ${target_price:.0f} (target reached)
</p>"""
    
    st.markdown(f"""
    <div style='padding: 2rem; background: {action_bg};
                backdrop-filter: blur(10px);
                border: 2px solid {action_border}; border-radius: 10px;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);'>
        {action_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Industry Positioning (Simple version for now)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.5rem; margin-bottom: 1rem;
               border-bottom: 2px solid rgba(59, 130, 246, 0.25); padding-bottom: 0.5rem;'>
        <i class="bi bi-building" style="margin-right: 0.5rem;"></i>COMPANY PROFILE
    </h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='padding: 1.5rem; background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.15) 100%);
                border-radius: 10px; border: 1px solid rgba(59, 130, 246, 0.25);'>
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; color: #e3f2fd;'>
            <div><strong style='color: #3b82f6;'>Company:</strong> {generator.company_name}</div>
            <div><strong style='color: #3b82f6;'>Ticker:</strong> {generator.ticker}</div>
            <div><strong style='color: #3b82f6;'>Analysis Date:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d')}</div>
            <div><strong style='color: #3b82f6;'>Report Type:</strong> Investment Summary</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer note
    st.markdown("<br>", unsafe_allow_html=True)
    
    # PDF Export Button
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <h3 style='color: #1e88e5; font-weight: 700; font-size: 1.3rem; margin-bottom: 1rem;
               text-align: center;'>
        <i class="bi bi-file-earmark-pdf-fill" style="margin-right: 0.5rem;"></i>EXPORT REPORT
    </h3>
    """, unsafe_allow_html=True)
    
    export_col1, export_col2, export_col3 = st.columns([1, 2, 1])
    
    with export_col2:
        # PDF type selector
        pdf_type = st.radio(
            "Report Type",
            ["Standard IC Memo", "Enhanced (with Alpha Signals)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if st.button("📄 Download PDF Report", use_container_width=True, type="primary"):
            try:
                if pdf_type == "Enhanced (with Alpha Signals)":
                    # Use enhanced PDF export with alpha signals
                    from pdf_export_enhanced import generate_enhanced_ic_memo, get_alpha_data_for_pdf
                    
                    # Get alpha signals data
                    alpha_data = get_alpha_data_for_pdf(generator.ticker)
                    
                    # Calculate scores
                    conviction_map = {'LOW': 33, 'MEDIUM': 66, 'HIGH': 100}
                    scores = {
                        'conviction': conviction_map.get(recommendation_data.get('conviction', 'MEDIUM'), 50),
                        'health': _calculate_health_score(financials),
                        'risk_reward': min(100, max(0, recommendation_data.get('risk_reward', 1.0) * 40)),
                        'earnings_momentum': alpha_data.get('earnings', {}).get('momentum_score'),
                        'insider_sentiment': alpha_data.get('insider', {}).get('sentiment_score'),
                        'institutional_accumulation': alpha_data.get('ownership', {}).get('accumulation_score'),
                    }
                    
                    # Get additional data
                    investment_thesis = generator.generate_investment_thesis()
                    catalysts = generator.generate_catalyst_timeline()
                    risks = generator.triage_red_flags()
                    comparables = generator.generate_peer_comparison()
                    
                    # Build key metrics
                    info = financials.get('info', {})
                    key_metrics = {
                        'Current Price': f"${info.get('currentPrice', info.get('regularMarketPrice', 0)):.2f}",
                        'P/E Ratio': f"{info.get('trailingPE', 'N/A')}x" if info.get('trailingPE') else 'N/A',
                        'Market Cap': f"${info.get('marketCap', 0)/1e9:.1f}B" if info.get('marketCap') else 'N/A',
                        'ROE': f"{info.get('returnOnEquity', 0)*100:.1f}%" if info.get('returnOnEquity') else 'N/A',
                        'Revenue (TTM)': f"${info.get('totalRevenue', 0)/1e9:.1f}B" if info.get('totalRevenue') else 'N/A',
                    }
                    
                    pdf_buffer = generate_enhanced_ic_memo(
                        ticker=generator.ticker,
                        company_name=generator.company_name,
                        recommendation_data=recommendation_data,
                        scores=scores,
                        alpha_data=alpha_data if alpha_data else None,
                        investment_thesis=investment_thesis,
                        catalysts=catalysts,
                        risks=risks,
                        comparables=comparables,
                        key_metrics=key_metrics
                    )
                    
                    filename = f"IC_Memo_Enhanced_{generator.ticker}_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf"
                else:
                    # Use standard PDF export
                    from pdf_export import generate_investment_summary_pdf
                    pdf_buffer = generate_investment_summary_pdf(financials, generator, recommendation_data)
                    filename = f"Investment_Summary_{generator.ticker}_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf"
                
                # Download button
                st.download_button(
                    label="💾 Save PDF Report",
                    data=pdf_buffer,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.success("✅ PDF generated successfully! Click 'Save' button above to download.")
                
            except ImportError as e:
                st.error("⚠️ PDF export requires 'reportlab' library. Install with: pip install reportlab")
            except Exception as e:
                st.error(f"❌ PDF generation error: {e}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #3b82f6; font-size: 0.9rem;
                border-top: 1px solid rgba(59, 130, 246, 0.15); margin-top: 2rem;'>
        <em>This analysis is for informational purposes only and should not be considered investment advice.</em>
    </div>
    """, unsafe_allow_html=True)

