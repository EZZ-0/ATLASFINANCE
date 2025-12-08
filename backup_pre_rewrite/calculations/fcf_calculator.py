"""
Free Cash Flow Calculator for ATLAS Financial Intelligence
============================================================

Provides multiple FCF calculation methods for different use cases:
1. Simple FCF: OCF - CapEx
2. Levered FCF: OCF - CapEx - Interest
3. Owner Earnings (Buffett): NI + D&A - CapEx - ΔWC
4. FCFF (Free Cash Flow to Firm): EBIT(1-T) + D&A - CapEx - ΔWC

Author: ATLAS Financial Intelligence
Date: 2025-12-07
"""

from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FCFMethod(Enum):
    """Available FCF calculation methods."""
    SIMPLE = "simple"
    LEVERED = "levered"
    OWNER_EARNINGS = "owner_earnings"
    FCFF = "fcff"


@dataclass
class FCFResult:
    """Result of an FCF calculation."""
    method: FCFMethod
    value: float
    components: Dict[str, float]
    formula: str
    description: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'method': self.method.value,
            'value': self.value,
            'components': self.components,
            'formula': self.formula,
            'description': self.description
        }


class FCFCalculator:
    """
    Calculator for multiple Free Cash Flow methodologies.
    
    Usage:
        calc = FCFCalculator(financials)
        simple = calc.calculate_simple_fcf()
        all_methods = calc.calculate_all()
    """
    
    def __init__(self, financials: Dict):
        """
        Initialize with financials dictionary.
        
        Expected fields (use None if not available):
        - operating_cash_flow / operatingCashflow
        - capital_expenditures / capitalExpenditures (positive = outflow)
        - interest_expense / interestExpense
        - net_income / netIncome
        - depreciation / depreciationAndAmortization
        - amortization (optional, may be combined with depreciation)
        - change_in_working_capital / changeInWorkingCapital
        - ebit / operatingIncome
        - tax_rate (or use default 21%)
        """
        self.financials = financials
        self._normalize_fields()
    
    def _normalize_fields(self):
        """Normalize field names to standard format."""
        self.ocf = self._get_value(['operating_cash_flow', 'operatingCashflow', 'OCF'])
        self.capex = abs(self._get_value(['capital_expenditures', 'capitalExpenditures', 'capex', 'CapEx']) or 0)
        self.interest = self._get_value(['interest_expense', 'interestExpense']) or 0
        self.net_income = self._get_value(['net_income', 'netIncome', 'NI'])
        self.depreciation = self._get_value(['depreciation', 'depreciationAndAmortization', 'D&A']) or 0
        self.amortization = self._get_value(['amortization']) or 0
        self.wc_change = self._get_value(['change_in_working_capital', 'changeInWorkingCapital', 'delta_wc']) or 0
        self.ebit = self._get_value(['ebit', 'operatingIncome', 'operating_income', 'EBIT'])
        self.tax_rate = self._get_value(['tax_rate', 'effectiveTaxRate']) or 0.21
    
    def _get_value(self, possible_keys: list) -> Optional[float]:
        """Get value from financials using possible key names."""
        for key in possible_keys:
            if key in self.financials and self.financials[key] is not None:
                return float(self.financials[key])
        return None
    
    def calculate_simple_fcf(self) -> Optional[FCFResult]:
        """
        Calculate Simple FCF: Operating Cash Flow - Capital Expenditures
        
        Use case: Quick cash generation assessment
        Pros: Simple, widely used
        Cons: Ignores financing costs
        """
        if self.ocf is None:
            logger.warning("Cannot calculate Simple FCF: OCF not available")
            return None
        
        fcf = self.ocf - self.capex
        
        return FCFResult(
            method=FCFMethod.SIMPLE,
            value=fcf,
            components={
                'operating_cash_flow': self.ocf,
                'capital_expenditures': self.capex
            },
            formula="FCF = OCF - CapEx",
            description="Simple FCF measures cash generated after maintaining/expanding asset base"
        )
    
    def calculate_levered_fcf(self) -> Optional[FCFResult]:
        """
        Calculate Levered FCF: OCF - CapEx - Interest Expense
        
        Use case: Cash available to equity holders
        Pros: Shows true equity cash flow
        Cons: Affected by capital structure
        """
        if self.ocf is None:
            logger.warning("Cannot calculate Levered FCF: OCF not available")
            return None
        
        fcf = self.ocf - self.capex - self.interest
        
        return FCFResult(
            method=FCFMethod.LEVERED,
            value=fcf,
            components={
                'operating_cash_flow': self.ocf,
                'capital_expenditures': self.capex,
                'interest_expense': self.interest
            },
            formula="LFCF = OCF - CapEx - Interest",
            description="Levered FCF shows cash available to equity holders after debt service"
        )
    
    def calculate_owner_earnings(self) -> Optional[FCFResult]:
        """
        Calculate Owner Earnings (Buffett Method):
        Net Income + D&A - CapEx - Working Capital Change
        
        Use case: True economic earnings (Buffett's preferred)
        Pros: Accounts for maintenance capital
        Cons: Requires good WC data
        """
        if self.net_income is None:
            logger.warning("Cannot calculate Owner Earnings: Net Income not available")
            return None
        
        d_and_a = self.depreciation + self.amortization
        fcf = self.net_income + d_and_a - self.capex - self.wc_change
        
        return FCFResult(
            method=FCFMethod.OWNER_EARNINGS,
            value=fcf,
            components={
                'net_income': self.net_income,
                'depreciation': self.depreciation,
                'amortization': self.amortization,
                'capital_expenditures': self.capex,
                'working_capital_change': self.wc_change
            },
            formula="Owner Earnings = NI + D&A - CapEx - ΔWC",
            description="Warren Buffett's preferred measure of true owner cash flow"
        )
    
    def calculate_fcff(self) -> Optional[FCFResult]:
        """
        Calculate Free Cash Flow to Firm (FCFF):
        EBIT × (1 - Tax Rate) + D&A - CapEx - Working Capital Change
        
        Use case: Valuation (DCF), ignores capital structure
        Pros: Capital structure neutral
        Cons: Requires EBIT and tax rate
        """
        if self.ebit is None:
            logger.warning("Cannot calculate FCFF: EBIT not available")
            return None
        
        nopat = self.ebit * (1 - self.tax_rate)
        d_and_a = self.depreciation + self.amortization
        fcf = nopat + d_and_a - self.capex - self.wc_change
        
        return FCFResult(
            method=FCFMethod.FCFF,
            value=fcf,
            components={
                'ebit': self.ebit,
                'tax_rate': self.tax_rate,
                'nopat': nopat,
                'depreciation': self.depreciation,
                'amortization': self.amortization,
                'capital_expenditures': self.capex,
                'working_capital_change': self.wc_change
            },
            formula="FCFF = EBIT(1-T) + D&A - CapEx - ΔWC",
            description="Free Cash Flow to Firm - used in DCF valuation, capital structure neutral"
        )
    
    def calculate_all(self) -> Dict[str, Optional[FCFResult]]:
        """Calculate all FCF methods and return results."""
        return {
            'simple': self.calculate_simple_fcf(),
            'levered': self.calculate_levered_fcf(),
            'owner_earnings': self.calculate_owner_earnings(),
            'fcff': self.calculate_fcff()
        }
    
    def get_recommended_method(self) -> Tuple[FCFMethod, str]:
        """
        Recommend the best FCF method based on available data.
        
        Returns:
            Tuple of (recommended method, reason)
        """
        # Check data availability
        has_ocf = self.ocf is not None
        has_ebit = self.ebit is not None
        has_net_income = self.net_income is not None
        has_interest = self.interest > 0
        has_depreciation = self.depreciation > 0
        
        if has_ebit and has_depreciation:
            return (FCFMethod.FCFF, "FCFF recommended: EBIT available, best for valuation")
        elif has_net_income and has_depreciation:
            return (FCFMethod.OWNER_EARNINGS, "Owner Earnings recommended: NI and D&A available")
        elif has_ocf and has_interest:
            return (FCFMethod.LEVERED, "Levered FCF recommended: OCF and interest available")
        elif has_ocf:
            return (FCFMethod.SIMPLE, "Simple FCF: Only OCF available")
        else:
            return (FCFMethod.SIMPLE, "Default to Simple FCF: Limited data")
    
    @staticmethod
    def get_method_description(method: FCFMethod) -> str:
        """Get detailed description of an FCF method."""
        descriptions = {
            FCFMethod.SIMPLE: """
**Simple Free Cash Flow**
Formula: OCF - CapEx

Best for: Quick assessment of cash generation
Pros: Easy to calculate, widely understood
Cons: Ignores debt service and working capital needs

Use when: You want a basic view of operational cash generation.
            """,
            FCFMethod.LEVERED: """
**Levered Free Cash Flow**
Formula: OCF - CapEx - Interest Expense

Best for: Equity investors
Pros: Shows actual cash available to shareholders
Cons: Affected by financing decisions

Use when: Evaluating from an equity holder's perspective.
            """,
            FCFMethod.OWNER_EARNINGS: """
**Owner Earnings (Buffett Method)**
Formula: Net Income + D&A - CapEx - ΔWorking Capital

Best for: Long-term value investors
Pros: Approximates true economic earnings
Cons: Requires detailed financial data

Use when: Following Buffett-style value investing approach.
            """,
            FCFMethod.FCFF: """
**Free Cash Flow to Firm**
Formula: EBIT × (1 - Tax Rate) + D&A - CapEx - ΔWC

Best for: DCF valuation
Pros: Capital structure neutral
Cons: More complex calculation

Use when: Performing DCF analysis or comparing companies with different debt levels.
            """
        }
        return descriptions.get(method, "Unknown method")


def calculate_fcf(financials: Dict, method: FCFMethod = FCFMethod.FCFF) -> Optional[FCFResult]:
    """
    Convenience function to calculate FCF using specified method.
    
    Args:
        financials: Dictionary of financial data
        method: FCF calculation method to use
    
    Returns:
        FCFResult or None if calculation not possible
    """
    calc = FCFCalculator(financials)
    
    method_map = {
        FCFMethod.SIMPLE: calc.calculate_simple_fcf,
        FCFMethod.LEVERED: calc.calculate_levered_fcf,
        FCFMethod.OWNER_EARNINGS: calc.calculate_owner_earnings,
        FCFMethod.FCFF: calc.calculate_fcff
    }
    
    return method_map[method]()


def calculate_all_fcf(financials: Dict) -> Dict[str, Optional[FCFResult]]:
    """
    Calculate all FCF methods for given financials.
    
    Args:
        financials: Dictionary of financial data
    
    Returns:
        Dict with all FCF results
    """
    calc = FCFCalculator(financials)
    return calc.calculate_all()


# Example usage and testing
if __name__ == "__main__":
    # Sample AAPL-like data
    sample_financials = {
        'operating_cash_flow': 110_000_000_000,
        'capital_expenditures': 11_000_000_000,
        'interest_expense': 3_000_000_000,
        'net_income': 97_000_000_000,
        'depreciation': 11_000_000_000,
        'amortization': 500_000_000,
        'change_in_working_capital': -2_000_000_000,
        'ebit': 120_000_000_000,
        'tax_rate': 0.16
    }
    
    print("Testing FCF Calculator with sample data...\n")
    
    calc = FCFCalculator(sample_financials)
    results = calc.calculate_all()
    
    for name, result in results.items():
        if result:
            print(f"{result.method.value.upper()}")
            print(f"  Value: ${result.value:,.0f}")
            print(f"  Formula: {result.formula}")
            print(f"  Components: {result.components}")
            print()
    
    # Get recommendation
    recommended, reason = calc.get_recommended_method()
    print(f"Recommended method: {recommended.value}")
    print(f"Reason: {reason}")

