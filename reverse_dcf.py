"""
REVERSE DCF (EXPECTATIONS INVESTING)
================================================================================
Purpose: Calculate market-implied assumptions from current stock price
Strategy: Solve for Growth Rate, Margin, and WACC that justify current price
Author: Atlas Financial Intelligence
Date: November 28, 2025
================================================================================

Theory:
    Current Stock Price = f(Growth, Margin, WACC, Terminal Growth)
    
    Instead of predicting fair value, we ask:
    "What assumptions must be TRUE for the current price to be justified?"
    
    This reveals what the MARKET is pricing in, allowing investors to decide:
    "Do I agree with the market's expectations?"

Example:
    Stock trading at $180
    Reverse-DCF reveals: "Market expects 14% revenue growth for 10 years"
    Investor decides: "No way! Industry growing at 5%. Stock is overvalued."
"""

import numpy as np
from scipy.optimize import minimize_scalar, minimize
from typing import Dict, Optional, Tuple


class ReverseDCF:
    """
    Reverse DCF Calculator - Solves for market-implied assumptions
    """
    
    def __init__(self, financials: Dict):
        """
        Initialize with financial data
        
        Args:
            financials: Dictionary from quick_extract containing:
                - income_statement
                - balance_sheet
                - cash_flow
                - market_data (current price)
                - ratios
        """
        self.financials = financials
        self.current_price = self._get_current_price()
        self.shares_outstanding = self._get_shares_outstanding()
        
        # Extract base metrics
        self.revenue = self._get_latest_metric('income_statement', 
            ['Total Revenue', 'Total_Revenue'])
        self.operating_income = self._get_latest_metric('income_statement',
            ['Operating Income', 'Operating_Income', 'EBIT'])
        self.operating_margin = self.operating_income / self.revenue if self.revenue else 0.10
        
        self.cash_flow = self._get_latest_metric('cash_flow',
            ['Operating Cash Flow', 'Total Cash From Operating Activities'])
        self.capex = self._get_latest_metric('cash_flow',
            ['Capital Expenditure', 'Capital Expenditures', 'CapEx'])
        
        if self.capex is not None:
            self.capex = abs(self.capex)  # CapEx is usually negative
        
        # Balance sheet
        self.total_debt = self._get_latest_metric('balance_sheet',
            ['Total Debt', 'Total_Debt', 'Long Term Debt'])
        self.cash = self._get_latest_metric('balance_sheet',
            ['Cash And Cash Equivalents', 'Cash'])
        
        self.net_debt = (self.total_debt or 0) - (self.cash or 0)
        
    def _get_current_price(self) -> float:
        """Extract current stock price"""
        try:
            if 'market_data' in self.financials:
                if 'current_price' in self.financials['market_data']:
                    return float(self.financials['market_data']['current_price'])
                elif 'historical_prices' in self.financials['market_data']:
                    prices = self.financials['market_data']['historical_prices']
                    if not prices.empty:
                        return float(prices['Close'].iloc[-1])
            return None
        except:
            return None
    
    def _get_shares_outstanding(self) -> float:
        """Get shares outstanding"""
        try:
            if 'info' in self.financials:
                shares = self.financials['info'].get('sharesOutstanding')
                if shares:
                    return float(shares)
            
            # Fallback: try to infer from balance sheet
            balance = self.financials.get('balance_sheet')
            if balance is not None:
                if 'Share Issued' in balance.index:
                    return float(balance.loc['Share Issued'].iloc[0])
                elif 'Ordinary Shares Number' in balance.index:
                    return float(balance.loc['Ordinary Shares Number'].iloc[0])
            
            return None
        except:
            return None
    
    def _get_latest_metric(self, statement: str, field_names: list) -> Optional[float]:
        """Helper to extract latest value from financial statement"""
        try:
            df = self.financials.get(statement)
            if df is None or df.empty:
                return None
            
            for field in field_names:
                if field in df.index:
                    value = df.loc[field].iloc[0]
                    return float(value) if value is not None else None
            return None
        except:
            return None
    
    def solve_for_growth_rate(self, 
                               terminal_growth: float = 0.025,
                               wacc: float = 0.10,
                               projection_years: int = 10) -> Dict:
        """
        Solve for the revenue growth rate that justifies current stock price
        
        Args:
            terminal_growth: Terminal growth rate (default 2.5%)
            wacc: Discount rate (default 10%)
            projection_years: Number of years to project (default 10)
        
        Returns:
            Dictionary with:
                - implied_growth_rate: The growth rate market is pricing in
                - current_price: Current stock price
                - fair_value_at_implied_growth: Validation (should match current)
                - analysis: Interpretation
        """
        if self.current_price is None or self.shares_outstanding is None:
            return {
                'status': 'error',
                'message': 'Missing current price or shares outstanding'
            }
        
        if self.revenue is None or self.revenue <= 0:
            return {
                'status': 'error',
                'message': 'Missing or invalid revenue data'
            }
        
        # Target equity value
        target_equity_value = self.current_price * self.shares_outstanding
        target_enterprise_value = target_equity_value + self.net_debt
        
        def dcf_error(growth_rate):
            """Calculate DCF value for given growth rate and return error vs. target"""
            if growth_rate < -0.50 or growth_rate > 1.00:  # Bounds: -50% to +100%
                return 1e12  # Penalize unrealistic growth
            
            # Project cash flows
            revenue = self.revenue
            pv_cashflows = 0
            
            for year in range(1, projection_years + 1):
                revenue *= (1 + growth_rate)
                ebit = revenue * self.operating_margin
                tax_rate = 0.25  # Assume 25% tax
                nopat = ebit * (1 - tax_rate)
                
                # Estimate FCF (simplified: NOPAT - CapEx)
                capex_rate = (self.capex / self.revenue) if self.capex and self.revenue else 0.05
                capex = revenue * capex_rate
                fcf = nopat - capex
                
                # Discount
                pv_cashflows += fcf / ((1 + wacc) ** year)
            
            # Terminal value
            terminal_revenue = revenue * (1 + terminal_growth)
            terminal_ebit = terminal_revenue * self.operating_margin
            terminal_nopat = terminal_ebit * (1 - 0.25)
            terminal_capex = terminal_revenue * capex_rate if self.capex else terminal_revenue * 0.05
            terminal_fcf = terminal_nopat - terminal_capex
            
            terminal_value = terminal_fcf / (wacc - terminal_growth)
            pv_terminal = terminal_value / ((1 + wacc) ** projection_years)
            
            # Enterprise Value
            enterprise_value = pv_cashflows + pv_terminal
            
            # Error (squared difference)
            return (enterprise_value - target_enterprise_value) ** 2
        
        # Optimize to find growth rate
        result = minimize_scalar(dcf_error, bounds=(-0.20, 0.50), method='bounded')
        
        if not result.success:
            return {
                'status': 'error',
                'message': 'Optimization failed to converge'
            }
        
        implied_growth = result.x
        
        # Validate by calculating DCF at implied growth
        validation_dcf = self._calculate_dcf_at_growth(implied_growth, terminal_growth, wacc, projection_years)
        
        # Interpret
        analysis = self._interpret_implied_growth(implied_growth)
        
        return {
            'status': 'success',
            'implied_growth_rate': implied_growth,
            'current_price': self.current_price,
            'target_enterprise_value': target_enterprise_value / 1e9,  # In billions
            'calculated_enterprise_value': validation_dcf['enterprise_value'] / 1e9,
            'error_pct': abs(validation_dcf['enterprise_value'] - target_enterprise_value) / target_enterprise_value,
            'assumptions': {
                'wacc': wacc,
                'terminal_growth': terminal_growth,
                'projection_years': projection_years,
                'operating_margin': self.operating_margin,
            },
            'analysis': analysis,
            'recommendation': self._generate_recommendation(implied_growth)
        }
    
    def _calculate_dcf_at_growth(self, growth_rate: float, terminal_growth: float, 
                                  wacc: float, projection_years: int) -> Dict:
        """Calculate DCF value at specific growth rate"""
        revenue = self.revenue
        pv_cashflows = 0
        
        for year in range(1, projection_years + 1):
            revenue *= (1 + growth_rate)
            ebit = revenue * self.operating_margin
            nopat = ebit * 0.75  # 25% tax
            capex_rate = (self.capex / self.revenue) if self.capex and self.revenue else 0.05
            capex = revenue * capex_rate
            fcf = nopat - capex
            pv_cashflows += fcf / ((1 + wacc) ** year)
        
        # Terminal
        terminal_revenue = revenue * (1 + terminal_growth)
        terminal_fcf = (terminal_revenue * self.operating_margin * 0.75) - (terminal_revenue * capex_rate)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1 + wacc) ** projection_years)
        
        enterprise_value = pv_cashflows + pv_terminal
        
        return {
            'enterprise_value': enterprise_value,
            'pv_cashflows': pv_cashflows,
            'pv_terminal': pv_terminal
        }
    
    def _interpret_implied_growth(self, growth_rate: float) -> str:
        """Interpret the implied growth rate"""
        if growth_rate < 0:
            return f"Market expects DECLINING revenue ({growth_rate*100:.1f}% annually). Company in distress or turnaround."
        elif growth_rate < 0.03:
            return f"Market expects SLOW growth ({growth_rate*100:.1f}% annually). Mature, stable business."
        elif growth_rate < 0.08:
            return f"Market expects MODERATE growth ({growth_rate*100:.1f}% annually). Typical for established companies."
        elif growth_rate < 0.15:
            return f"Market expects HEALTHY growth ({growth_rate*100:.1f}% annually). Strong competitive position."
        elif growth_rate < 0.25:
            return f"Market expects HIGH growth ({growth_rate*100:.1f}% annually). Premium valuation."
        else:
            return f"Market expects EXTREME growth ({growth_rate*100:.1f}% annually). Very aggressive assumptions!"
    
    def _generate_recommendation(self, growth_rate: float) -> str:
        """Generate investment recommendation based on implied growth"""
        return (
            f"The market is pricing in {growth_rate*100:.1f}% annual revenue growth for the next 10 years.\n"
            f"Ask yourself: Can this company realistically achieve this growth rate?\n"
            f"If YES -> Stock is fairly valued or undervalued.\n"
            f"If NO -> Stock is overvalued relative to realistic expectations."
        )
    
    def solve_for_multiple_variables(self) -> Dict:
        """
        Solve for BOTH growth rate AND operating margin
        (More advanced - allows margin expansion/contraction)
        """
        if self.current_price is None or self.shares_outstanding is None:
            return {'status': 'error', 'message': 'Missing price data'}
        
        target_equity_value = self.current_price * self.shares_outstanding
        target_enterprise_value = target_equity_value + self.net_debt
        
        def dcf_error_2d(params):
            """Error function for 2D optimization (growth + margin)"""
            growth_rate, margin = params
            
            if growth_rate < -0.50 or growth_rate > 1.00:
                return 1e12
            if margin < 0.01 or margin > 0.50:
                return 1e12
            
            revenue = self.revenue
            pv_cashflows = 0
            wacc = 0.10
            terminal_growth = 0.025
            
            for year in range(1, 11):
                revenue *= (1 + growth_rate)
                ebit = revenue * margin
                nopat = ebit * 0.75
                capex_rate = (self.capex / self.revenue) if self.capex and self.revenue else 0.05
                fcf = nopat - (revenue * capex_rate)
                pv_cashflows += fcf / ((1 + wacc) ** year)
            
            # Terminal
            terminal_revenue = revenue * (1 + terminal_growth)
            terminal_fcf = (terminal_revenue * margin * 0.75) - (terminal_revenue * capex_rate)
            pv_terminal = (terminal_fcf / (wacc - terminal_growth)) / ((1 + wacc) ** 10)
            
            enterprise_value = pv_cashflows + pv_terminal
            return (enterprise_value - target_enterprise_value) ** 2
        
        # Optimize
        initial_guess = [0.05, self.operating_margin]
        result = minimize(dcf_error_2d, initial_guess, method='Nelder-Mead',
                          bounds=[(-0.20, 0.50), (0.01, 0.50)])
        
        if not result.success:
            return {'status': 'error', 'message': 'Optimization failed'}
        
        implied_growth, implied_margin = result.x
        
        return {
            'status': 'success',
            'implied_growth_rate': implied_growth,
            'implied_operating_margin': implied_margin,
            'current_margin': self.operating_margin,
            'margin_change_required': implied_margin - self.operating_margin,
            'current_price': self.current_price,
            'analysis': (
                f"Market expects {implied_growth*100:.1f}% growth AND "
                f"{implied_margin*100:.1f}% operating margin "
                f"(current: {self.operating_margin*100:.1f}%)."
            )
        }


def analyze_reverse_dcf(financials: Dict) -> Dict:
    """
    Main function to run Reverse DCF analysis
    
    Returns:
        Dictionary with:
            - Method 1: Solve for growth rate only
            - Method 2: Solve for growth + margin
            - Comparison and recommendations
    """
    rdcf = ReverseDCF(financials)
    
    # Method 1: Growth rate only
    result_growth = rdcf.solve_for_growth_rate()
    
    # Method 2: Growth + Margin
    result_both = rdcf.solve_for_multiple_variables()
    
    return {
        'method_1_growth_only': result_growth,
        'method_2_growth_and_margin': result_both,
        'summary': {
            'current_price': rdcf.current_price,
            'revenue_latest': rdcf.revenue / 1e9 if rdcf.revenue else None,
            'operating_margin_current': rdcf.operating_margin * 100 if rdcf.operating_margin else None,
        }
    }

