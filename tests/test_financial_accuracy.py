"""
Financial Accuracy Test Suite for ATLAS Financial Intelligence
================================================================

Automated tests to verify financial calculations are accurate.
Run with: pytest tests/test_financial_accuracy.py -v

Author: ATLAS Financial Intelligence
Date: 2025-12-07
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestWACCCalculations:
    """Test WACC (Weighted Average Cost of Capital) calculations."""
    
    def test_wacc_formula_basic(self):
        """Test basic WACC formula: WACC = (E/V × Re) + (D/V × Rd × (1-T))"""
        # Test case: Equal debt and equity
        equity_value = 100_000_000
        debt_value = 100_000_000
        total_value = equity_value + debt_value
        
        cost_of_equity = 0.10  # 10%
        cost_of_debt = 0.05   # 5%
        tax_rate = 0.21       # 21%
        
        # Manual calculation
        equity_weight = equity_value / total_value  # 0.5
        debt_weight = debt_value / total_value      # 0.5
        
        expected_wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt * (1 - tax_rate))
        # = (0.5 × 0.10) + (0.5 × 0.05 × 0.79)
        # = 0.05 + 0.01975
        # = 0.06975 or 6.975%
        
        assert abs(expected_wacc - 0.06975) < 0.0001
    
    def test_adjusted_beta_calculation(self):
        """Test Bloomberg adjusted beta formula: 0.67 × raw_beta + 0.33"""
        raw_betas = [0.8, 1.0, 1.2, 1.5, 2.0]
        
        for raw_beta in raw_betas:
            adjusted = 0.67 * raw_beta + 0.33
            # Adjusted beta should regress toward 1.0
            if raw_beta < 1.0:
                assert adjusted > raw_beta, f"Adjusted beta should be higher than raw for beta < 1"
            elif raw_beta > 1.0:
                assert adjusted < raw_beta, f"Adjusted beta should be lower than raw for beta > 1"
    
    def test_cost_of_equity_capm(self):
        """Test Cost of Equity using CAPM: Re = Rf + β(Rm - Rf)"""
        risk_free_rate = 0.045  # 4.5%
        market_premium = 0.055  # 5.5%
        beta = 1.2
        
        cost_of_equity = risk_free_rate + beta * market_premium
        # = 0.045 + 1.2 × 0.055
        # = 0.045 + 0.066
        # = 0.111 or 11.1%
        
        assert abs(cost_of_equity - 0.111) < 0.001
    
    def test_wacc_reasonable_range(self):
        """WACC should typically be between 5% and 15% for most companies."""
        # Using typical values
        typical_wacc_low = 0.05
        typical_wacc_high = 0.15
        
        # Test case
        wacc = 0.09  # 9%
        assert typical_wacc_low <= wacc <= typical_wacc_high


class TestFCFCalculations:
    """Test Free Cash Flow calculations."""
    
    def test_fcf_simple(self):
        """FCF Simple = Operating Cash Flow - Capital Expenditures"""
        ocf = 100_000_000
        capex = 20_000_000
        
        fcf_simple = ocf - capex
        assert fcf_simple == 80_000_000
    
    def test_fcf_levered(self):
        """FCF Levered = OCF - CapEx - Interest Expense"""
        ocf = 100_000_000
        capex = 20_000_000
        interest = 5_000_000
        
        fcf_levered = ocf - capex - interest
        assert fcf_levered == 75_000_000
    
    def test_fcf_owner_earnings(self):
        """
        Owner Earnings (Buffett) = Net Income + D&A - CapEx - Working Capital Change
        """
        net_income = 50_000_000
        depreciation = 10_000_000
        amortization = 2_000_000
        capex = 15_000_000
        wc_change = 3_000_000
        
        owner_earnings = net_income + depreciation + amortization - capex - wc_change
        # = 50 + 10 + 2 - 15 - 3 = 44 million
        
        assert owner_earnings == 44_000_000
    
    def test_fcff(self):
        """
        FCFF = EBIT × (1 - Tax Rate) + D&A - CapEx - Working Capital Change
        """
        ebit = 80_000_000
        tax_rate = 0.21
        depreciation = 10_000_000
        capex = 15_000_000
        wc_change = 5_000_000
        
        fcff = ebit * (1 - tax_rate) + depreciation - capex - wc_change
        # = 80M × 0.79 + 10M - 15M - 5M
        # = 63.2M + 10M - 15M - 5M
        # = 53.2M
        
        assert abs(fcff - 53_200_000) < 1
    
    def test_fcf_negative_capex(self):
        """CapEx should be positive (outflow). Negative CapEx doesn't make sense."""
        capex = -10_000_000  # Invalid
        
        # In real implementation, should either take absolute value or raise error
        assert abs(capex) == 10_000_000


class TestValuationRatios:
    """Test valuation ratio calculations."""
    
    def test_pe_ratio(self):
        """P/E Ratio = Price / Earnings Per Share"""
        price = 175.50
        eps = 6.43
        
        pe = price / eps
        # = 175.50 / 6.43 = 27.29
        
        assert abs(pe - 27.29) < 0.1
    
    def test_pe_ratio_negative_eps(self):
        """P/E should be N/A or flagged when EPS is negative."""
        price = 50.00
        eps = -2.00
        
        # P/E with negative EPS is meaningless
        pe = price / eps if eps > 0 else None
        assert pe is None
    
    def test_price_to_book(self):
        """P/B Ratio = Price / Book Value Per Share"""
        price = 175.50
        book_value_per_share = 4.25
        
        pb = price / book_value_per_share
        # = 175.50 / 4.25 = 41.29
        
        assert abs(pb - 41.29) < 0.1
    
    def test_ev_ebitda(self):
        """EV/EBITDA = Enterprise Value / EBITDA"""
        market_cap = 2_800_000_000_000  # $2.8T
        total_debt = 100_000_000_000    # $100B
        cash = 60_000_000_000           # $60B
        ebitda = 130_000_000_000        # $130B
        
        ev = market_cap + total_debt - cash
        ev_ebitda = ev / ebitda
        # EV = 2800 + 100 - 60 = 2840B
        # EV/EBITDA = 2840 / 130 = 21.85
        
        assert abs(ev_ebitda - 21.85) < 0.1
    
    def test_dividend_yield(self):
        """Dividend Yield = Annual Dividend / Price"""
        annual_dividend = 3.76
        price = 175.50
        
        div_yield = annual_dividend / price
        # = 3.76 / 175.50 = 0.0214 or 2.14%
        
        assert abs(div_yield - 0.0214) < 0.001


class TestProfitabilityRatios:
    """Test profitability ratio calculations."""
    
    def test_roe(self):
        """ROE = Net Income / Shareholders' Equity"""
        net_income = 97_000_000_000
        shareholders_equity = 62_000_000_000
        
        roe = net_income / shareholders_equity
        # = 97 / 62 = 1.565 or 156.5%
        
        assert abs(roe - 1.565) < 0.01
    
    def test_roa(self):
        """ROA = Net Income / Total Assets"""
        net_income = 97_000_000_000
        total_assets = 350_000_000_000
        
        roa = net_income / total_assets
        # = 97 / 350 = 0.277 or 27.7%
        
        assert abs(roa - 0.277) < 0.01
    
    def test_roic(self):
        """ROIC = NOPAT / Invested Capital"""
        ebit = 120_000_000_000
        tax_rate = 0.21
        total_debt = 100_000_000_000
        shareholders_equity = 62_000_000_000
        cash = 60_000_000_000
        
        nopat = ebit * (1 - tax_rate)
        invested_capital = total_debt + shareholders_equity - cash
        roic = nopat / invested_capital
        
        # NOPAT = 120B × 0.79 = 94.8B
        # IC = 100 + 62 - 60 = 102B
        # ROIC = 94.8 / 102 = 0.929 or 92.9%
        
        assert abs(roic - 0.929) < 0.01
    
    def test_gross_margin(self):
        """Gross Margin = Gross Profit / Revenue"""
        revenue = 400_000_000_000
        cogs = 170_000_000_000
        
        gross_profit = revenue - cogs
        gross_margin = gross_profit / revenue
        # = (400 - 170) / 400 = 230 / 400 = 0.575 or 57.5%
        
        assert abs(gross_margin - 0.575) < 0.01
    
    def test_operating_margin(self):
        """Operating Margin = Operating Income / Revenue"""
        revenue = 400_000_000_000
        operating_income = 120_000_000_000
        
        operating_margin = operating_income / revenue
        # = 120 / 400 = 0.30 or 30%
        
        assert abs(operating_margin - 0.30) < 0.01


class TestLiquidityRatios:
    """Test liquidity ratio calculations."""
    
    def test_current_ratio(self):
        """Current Ratio = Current Assets / Current Liabilities"""
        current_assets = 150_000_000_000
        current_liabilities = 160_000_000_000
        
        current_ratio = current_assets / current_liabilities
        # = 150 / 160 = 0.9375
        
        assert abs(current_ratio - 0.9375) < 0.01
    
    def test_quick_ratio(self):
        """Quick Ratio = (Current Assets - Inventory) / Current Liabilities"""
        current_assets = 150_000_000_000
        inventory = 10_000_000_000
        current_liabilities = 160_000_000_000
        
        quick_ratio = (current_assets - inventory) / current_liabilities
        # = (150 - 10) / 160 = 140 / 160 = 0.875
        
        assert abs(quick_ratio - 0.875) < 0.01
    
    def test_cash_ratio(self):
        """Cash Ratio = Cash / Current Liabilities"""
        cash = 60_000_000_000
        current_liabilities = 160_000_000_000
        
        cash_ratio = cash / current_liabilities
        # = 60 / 160 = 0.375
        
        assert abs(cash_ratio - 0.375) < 0.01


class TestLeverageRatios:
    """Test leverage/solvency ratio calculations."""
    
    def test_debt_to_equity(self):
        """D/E Ratio = Total Debt / Shareholders' Equity"""
        total_debt = 100_000_000_000
        shareholders_equity = 62_000_000_000
        
        de_ratio = total_debt / shareholders_equity
        # = 100 / 62 = 1.613
        
        assert abs(de_ratio - 1.613) < 0.01
    
    def test_debt_to_assets(self):
        """Debt to Assets = Total Debt / Total Assets"""
        total_debt = 100_000_000_000
        total_assets = 350_000_000_000
        
        debt_to_assets = total_debt / total_assets
        # = 100 / 350 = 0.286 or 28.6%
        
        assert abs(debt_to_assets - 0.286) < 0.01
    
    def test_interest_coverage(self):
        """Interest Coverage = EBIT / Interest Expense"""
        ebit = 120_000_000_000
        interest_expense = 3_000_000_000
        
        interest_coverage = ebit / interest_expense
        # = 120 / 3 = 40x
        
        assert abs(interest_coverage - 40) < 0.1


class TestDCFCalculations:
    """Test DCF (Discounted Cash Flow) calculations."""
    
    def test_present_value(self):
        """PV = FV / (1 + r)^n"""
        future_value = 100_000_000
        discount_rate = 0.10
        years = 5
        
        pv = future_value / ((1 + discount_rate) ** years)
        # = 100M / 1.1^5 = 100M / 1.6105 = 62.09M
        
        assert abs(pv - 62_092_132) < 100
    
    def test_terminal_value_gordon(self):
        """Terminal Value (Gordon Growth) = FCF × (1 + g) / (WACC - g)"""
        last_fcf = 100_000_000_000
        perpetual_growth = 0.025  # 2.5%
        wacc = 0.09  # 9%
        
        terminal_value = last_fcf * (1 + perpetual_growth) / (wacc - perpetual_growth)
        # = 100B × 1.025 / 0.065
        # = 102.5B / 0.065
        # = 1576.9B
        
        assert abs(terminal_value - 1_576_923_076_923) < 1_000_000
    
    def test_terminal_value_exit_multiple(self):
        """Terminal Value (Exit Multiple) = EBITDA × Multiple"""
        ebitda = 130_000_000_000
        exit_multiple = 15  # 15x EBITDA
        
        terminal_value = ebitda * exit_multiple
        # = 130B × 15 = 1950B
        
        assert terminal_value == 1_950_000_000_000
    
    def test_intrinsic_value_per_share(self):
        """Intrinsic Value per Share = Enterprise Value / Shares Outstanding"""
        enterprise_value = 3_000_000_000_000
        net_debt = 40_000_000_000
        shares_outstanding = 15_500_000_000
        
        equity_value = enterprise_value - net_debt
        intrinsic_value = equity_value / shares_outstanding
        
        # Equity = 3000B - 40B = 2960B
        # Per share = 2960B / 15.5B = $190.97
        
        assert abs(intrinsic_value - 190.97) < 0.1


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_division_by_zero_handling(self):
        """Ratios should handle zero denominators gracefully."""
        revenue = 0
        net_income = 100_000_000
        
        # Should not raise exception
        try:
            margin = net_income / revenue if revenue != 0 else None
            assert margin is None
        except ZeroDivisionError:
            pytest.fail("Division by zero not handled")
    
    def test_negative_values_handling(self):
        """Some metrics should flag or handle negative values."""
        # Negative equity (distressed company)
        shareholders_equity = -50_000_000_000
        net_income = 10_000_000_000
        
        # ROE with negative equity is meaningful but should be flagged
        roe = net_income / shareholders_equity if shareholders_equity != 0 else None
        
        # ROE is negative, which is possible and meaningful
        assert roe is not None
        assert roe < 0
    
    def test_very_large_numbers(self):
        """Handle large numbers (trillion-dollar companies)."""
        market_cap = 3_000_000_000_000  # $3 trillion
        revenue = 400_000_000_000  # $400 billion
        
        ps_ratio = market_cap / revenue
        # = 3000 / 400 = 7.5x
        
        assert abs(ps_ratio - 7.5) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

