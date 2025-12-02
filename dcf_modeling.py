"""
3-SCENARIO DCF MODELING ENGINE
===============================
Implements comprehensive Discounted Cash Flow valuation with:
1. Conservative Scenario (Bear Case)
2. Base Case Scenario (Most Likely)
3. Aggressive Scenario (Bull Case)

Methodology:
- Free Cash Flow projection (5-10 years)
- Terminal Value calculation
- WACC-based discounting
- Sensitivity analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import usa_dictionary as usa_dict

@dataclass
class DCFAssumptions:
    """Container for DCF model assumptions"""
    revenue_growth_rates: List[float]  # Year-by-year growth
    terminal_growth_rate: float
    discount_rate: float
    tax_rate: float
    capex_pct_revenue: float
    nwc_pct_revenue: float
    depreciation_pct_revenue: float
    projection_years: int
    wacc_source: str = "manual"  # "manual" or "calculated"
    
    def __repr__(self):
        return f"DCF({self.projection_years}Y, Terminal: {self.terminal_growth_rate:.1%}, WACC: {self.discount_rate:.1%})"
    
    def get_wacc_warning(self) -> str:
        """Return warning if WACC is manually set without calculation"""
        if self.wacc_source == "manual":
            return "⚠️ WARNING: Using fixed WACC. For more accuracy, consider calculating from Cost of Equity (CAPM) + Cost of Debt weighted by capital structure."
        return ""

class DCFModel:
    """
    Three-Scenario DCF Valuation Model
    
    Features:
    - Conservative/Base/Aggressive scenarios
    - Customizable assumptions
    - Sensitivity tables
    - Detailed cash flow projections
    """
    
    def __init__(self, financials: Dict):
        """
        Initialize DCF model with financial data.
        
        Args:
            financials: Output from usa_backend.extract_financials()
        """
        self.financials = financials
        self.ticker = financials.get("ticker", "UNKNOWN")
        
        # Extract base metrics from latest year
        self._extract_base_metrics()
        
        # Pre-built scenarios
        conservative = self._build_conservative_assumptions()
        base = self._build_base_assumptions()
        aggressive = self._build_aggressive_assumptions()
        
        self.scenarios = {
            "conservative": conservative,
            "base": base,
            "aggressive": aggressive,
            # Aliases for compatibility
            "bear": conservative,
            "bull": aggressive
        }
    
    # ==========================================
    # 1. DATA PREPARATION
    # ==========================================
    
    def _find_metric_value(self, df, keywords, latest_col=None):
        """
        Helper to find metric value from either SEC or yfinance format
        
        Args:
            df: DataFrame (income, balance, or cashflow)
            keywords: List of possible metric names
            latest_col: Column name for yfinance format (optional)
        
        Returns:
            float: metric value or 0 if not found
        """
        if df.empty:
            return 0
        
        try:
            # Check if yfinance format (rows are metrics)
            if len(df.index) > 0 and isinstance(df.index[0], str):
                # yfinance format
                if latest_col is None:
                    latest_col = df.columns[0]
                
                # Try exact match first (case-insensitive)
                for kw in keywords:
                    for idx in df.index:
                        if str(idx).lower().strip() == kw.lower().strip():
                            return float(df.loc[idx, latest_col]) if idx in df.index else 0
                
                # Then try partial match (contains)
                for kw in keywords:
                    for idx in df.index:
                        idx_lower = str(idx).lower()
                        if kw.lower() in idx_lower:
                            return float(df.loc[idx, latest_col]) if idx in df.index else 0
            else:
                # SEC format (columns are metrics)
                latest = df.iloc[0]
                for kw in keywords:
                    if kw in latest.index:
                        return float(latest.get(kw, 0))
        except:
            pass
        
        return 0
    
    def _extract_base_metrics(self):
        """Extract starting metrics from financial statements - handles both SEC and yfinance formats"""
        try:
            # Income Statement
            income = self.financials.get("income_statement", pd.DataFrame())
            if not income.empty:
                self.base_revenue = self._find_metric_value(
                    income, 
                    ["Total Revenue", "Revenue", "Net Sales", "Sales"]
                )
                self.base_operating_income = self._find_metric_value(
                    income,
                    ["Operating_Income", "Operating Income", "EBIT", "Operating Profit"]
                )
                self.base_net_income = self._find_metric_value(
                    income,
                    ["Net_Income", "Net Income"]
                )
                
                # Calculate margins
                if self.base_revenue > 0:
                    self.operating_margin = self.base_operating_income / self.base_revenue
                else:
                    self.operating_margin = 0.15  # Default 15%
            else:
                self.base_revenue = 0
                self.operating_margin = 0.15
            
            # Cash Flow Statement
            cashflow = self.financials.get("cash_flow", pd.DataFrame())
            if not cashflow.empty:
                self.base_ocf = self._find_metric_value(
                    cashflow,
                    ["Operating_Cash_Flow", "Total Cash From Operating Activities", "Operating Cash Flow"]
                )
                capex = self._find_metric_value(
                    cashflow,
                    ["Capex", "Capital Expenditures", "Capital Expenditure"]
                )
                self.base_capex = abs(capex)
                
                # Calculate % of revenue
                if self.base_revenue > 0:
                    self.capex_pct = self.base_capex / self.base_revenue
                else:
                    self.capex_pct = 0.05  # Default 5%
            else:
                self.base_ocf = 0
                self.base_capex = 0
                self.capex_pct = 0.05
            
            # Balance Sheet
            balance = self.financials.get("balance_sheet", pd.DataFrame())
            if not balance.empty:
                self.total_debt = self._find_metric_value(
                    balance,
                    ["Total_Debt", "Total Debt", "Long Term Debt", "Total Liabilities"]
                )
                self.cash = self._find_metric_value(
                    balance,
                    ["Cash", "Cash And Cash Equivalents", "Cash Equivalents"]
                )
            else:
                self.total_debt = 0
                self.cash = 0
            
            # Shares Outstanding (for per-share value)
            per_share = self.financials.get("per_share_data", pd.DataFrame())
            if not per_share.empty:
                latest_shares = per_share.iloc[0]
                self.shares_outstanding = latest_shares.get("Shares_Outstanding", 0)
            else:
                # Try to get from info (yfinance)
                info = self.financials.get("info", {})
                self.shares_outstanding = info.get("sharesOutstanding", 1_000_000_000)
            
            # Historical growth rate (for intelligent defaults)
            self.historical_growth = self._calculate_historical_growth()
            
        except Exception as e:
            print(f"⚠️ Metric extraction warning: {e}")
            self._set_default_metrics()
    
    def _calculate_historical_growth(self) -> float:
        """Calculate historical revenue CAGR for intelligent assumptions"""
        try:
            income = self.financials.get("income_statement", pd.DataFrame())
            if income.empty:
                return 0.10  # Default 10%
            
            # Handle yfinance format (rows are metrics)
            if len(income.index) > 0 and isinstance(income.index[0], str):
                # Find revenue row (prioritize "Total Revenue")
                revenue_row = None
                for idx in income.index:
                    idx_lower = str(idx).lower()
                    if 'total revenue' in idx_lower:
                        revenue_row = idx
                        break
                    elif 'net sales' in idx_lower and revenue_row is None:
                        revenue_row = idx
                    elif ('revenue' in idx_lower or 'sales' in idx_lower) and 'cost' not in idx_lower and revenue_row is None:
                        revenue_row = idx
                
                if revenue_row is None:
                    return 0.10
                
                revenues = income.loc[revenue_row].dropna()
            else:
                # SEC format
                if "Revenue" not in income.columns:
                    return 0.10
                revenues = income["Revenue"].dropna()
            
            if len(revenues) < 2:
                return 0.10
            
            # CAGR calculation (revenues are already sorted, most recent first)
            latest = float(revenues.iloc[0])
            oldest = float(revenues.iloc[-1])
            years = len(revenues) - 1
            
            if oldest > 0 and latest > 0:
                cagr = (latest / oldest) ** (1 / years) - 1
                # Cap at reasonable range (-10% to 50%)
                return max(-0.10, min(0.50, cagr))
            
            return 0.10
        except Exception as e:
            print(f"[WARN] Growth calculation failed: {e}")
            return 0.10
    
    def _set_default_metrics(self):
        """Set default values if extraction fails"""
        self.base_revenue = 1_000_000_000  # $1B default
        self.operating_margin = 0.15
        self.base_ocf = 0
        self.base_capex = 0
        self.capex_pct = 0.05
        self.total_debt = 0
        self.cash = 0
        self.shares_outstanding = 1_000_000_000
        self.historical_growth = 0.10
    
    # ==========================================
    # 2. ASSUMPTION BUILDERS
    # ==========================================
    
    def _build_conservative_assumptions(self) -> DCFAssumptions:
        """Conservative (Bear Case) assumptions"""
        # Lower growth, higher discount rate
        growth = max(0.03, self.historical_growth * 0.6)  # 60% of historical
        
        return DCFAssumptions(
            revenue_growth_rates=[growth] * 5,  # Flat conservative growth
            terminal_growth_rate=0.02,  # GDP growth
            discount_rate=0.12,  # Higher risk
            tax_rate=0.21,
            capex_pct_revenue=self.capex_pct * 1.2,  # Higher capex needs
            nwc_pct_revenue=0.05,
            depreciation_pct_revenue=0.04,
            projection_years=5
        )
    
    def _build_base_assumptions(self) -> DCFAssumptions:
        """Base Case (Most Likely) assumptions"""
        # Use historical growth or reasonable default
        growth = self.historical_growth if self.historical_growth > 0 else 0.10
        
        return DCFAssumptions(
            revenue_growth_rates=[growth] * 5,
            terminal_growth_rate=0.025,  # Slightly above GDP
            discount_rate=0.10,  # Standard WACC
            tax_rate=0.21,
            capex_pct_revenue=self.capex_pct,
            nwc_pct_revenue=0.03,
            depreciation_pct_revenue=0.04,
            projection_years=5
        )
    
    def _build_aggressive_assumptions(self) -> DCFAssumptions:
        """Aggressive (Bull Case) assumptions"""
        # Higher growth, lower discount rate
        growth = min(0.25, self.historical_growth * 1.5)  # 150% of historical, capped
        
        return DCFAssumptions(
            revenue_growth_rates=[growth] * 5,
            terminal_growth_rate=0.03,  # Optimistic perpetual growth
            discount_rate=0.08,  # Lower risk/higher confidence
            tax_rate=0.21,
            capex_pct_revenue=self.capex_pct * 0.8,  # Efficiency gains
            nwc_pct_revenue=0.02,
            depreciation_pct_revenue=0.04,
            projection_years=5
        )
    
    # ==========================================
    # 3. CORE DCF CALCULATION
    # ==========================================
    
    def calculate_dcf(self, scenario: str = "base", custom_assumptions: Optional[DCFAssumptions] = None) -> Dict:
        """
        Calculate DCF valuation for given scenario.
        
        Args:
            scenario: "conservative", "base", or "aggressive"
            custom_assumptions: Override with custom assumptions
            
        Returns:
            Dictionary with valuation results and detailed projections
        """
        # Get assumptions
        if custom_assumptions:
            assumptions = custom_assumptions
        else:
            assumptions = self.scenarios.get(scenario, self.scenarios["base"])
        
        print(f"\n[INFO] Running DCF Model: {scenario.upper()} | {assumptions}")
        
        # Build projection DataFrame
        projections = self._project_cash_flows(assumptions)
        
        # Calculate Terminal Value
        terminal_value = self._calculate_terminal_value(projections, assumptions)
        
        # Discount everything to present value
        pv_cash_flows = self._discount_cash_flows(projections, assumptions)
        pv_terminal_value = terminal_value / ((1 + assumptions.discount_rate) ** assumptions.projection_years)
        
        # Enterprise Value
        enterprise_value = pv_cash_flows.sum() + pv_terminal_value
        
        # Equity Value (EV - Net Debt)
        net_debt = self.total_debt - self.cash
        equity_value = enterprise_value - net_debt
        
        # Per-Share Value
        value_per_share = equity_value / self.shares_outstanding if self.shares_outstanding > 0 else 0
        
        return {
            "scenario": scenario,
            "assumptions": assumptions,
            "enterprise_value": enterprise_value,
            "equity_value": equity_value,
            "value_per_share": value_per_share,
            "equity_value_per_share": value_per_share,  # Alias for compatibility
            "pv_cashflows": pv_cash_flows.sum(),  # Match test expectation
            "pv_cash_flows": pv_cash_flows.sum(),  # Alternative key
            "pv_terminal_value": pv_terminal_value,
            "terminal_value": terminal_value,
            "net_debt": net_debt,
            "projections": projections,
            "shares_outstanding": self.shares_outstanding
        }
    
    def _project_cash_flows(self, assumptions: DCFAssumptions) -> pd.DataFrame:
        """
        Project Free Cash Flows for the forecast period.
        
        Returns DataFrame with yearly projections.
        """
        years = assumptions.projection_years
        projections = []
        
        # Starting point
        current_revenue = self.base_revenue
        
        for year in range(1, years + 1):
            # Revenue growth
            growth_idx = min(year - 1, len(assumptions.revenue_growth_rates) - 1)
            growth_rate = assumptions.revenue_growth_rates[growth_idx]
            revenue = current_revenue * (1 + growth_rate)
            
            # EBIT (using operating margin)
            ebit = revenue * self.operating_margin
            
            # Tax
            tax = ebit * assumptions.tax_rate
            
            # NOPAT (Net Operating Profit After Tax)
            nopat = ebit - tax
            
            # Add back Depreciation (non-cash)
            depreciation = revenue * assumptions.depreciation_pct_revenue
            
            # Subtract Capex (cash outflow)
            capex = revenue * assumptions.capex_pct_revenue
            
            # Subtract Change in Net Working Capital
            nwc_change = revenue * growth_rate * assumptions.nwc_pct_revenue
            
            # FREE CASH FLOW
            fcf = nopat + depreciation - capex - nwc_change
            
            projections.append({
                "Year": year,
                "Revenue": revenue,
                "EBIT": ebit,
                "Tax": tax,
                "NOPAT": nopat,
                "Depreciation": depreciation,
                "Capex": capex,
                "NWC_Change": nwc_change,
                "Free_Cash_Flow": fcf
            })
            
            # Update for next iteration
            current_revenue = revenue
        
        return pd.DataFrame(projections)
    
    def _calculate_terminal_value(self, projections: pd.DataFrame, assumptions: DCFAssumptions) -> float:
        """
        Calculate Terminal Value using Perpetual Growth Method.
        
        TV = FCF_final * (1 + g) / (WACC - g)
        """
        # Get final year FCF
        final_fcf = projections.iloc[-1]["Free_Cash_Flow"]
        
        # Grow by terminal rate
        terminal_fcf = final_fcf * (1 + assumptions.terminal_growth_rate)
        
        # Perpetuity formula
        terminal_value = terminal_fcf / (assumptions.discount_rate - assumptions.terminal_growth_rate)
        
        return terminal_value
    
    def _discount_cash_flows(self, projections: pd.DataFrame, assumptions: DCFAssumptions) -> pd.Series:
        """
        Discount projected FCFs to present value.
        
        PV = FCF / (1 + WACC)^year
        """
        discount_factors = [(1 + assumptions.discount_rate) ** year for year in projections["Year"]]
        pv_fcf = projections["Free_Cash_Flow"] / discount_factors
        
        return pv_fcf
    
    # ==========================================
    # 4. RUN ALL SCENARIOS
    # ==========================================
    
    def run_all_scenarios(self) -> Dict:
        """
        Run all three scenarios and return comprehensive results.
        
        Returns:
            Dictionary with results for all scenarios
        """
        print(f"\n{'='*60}")
        print(f"  3-SCENARIO DCF VALUATION: {self.ticker}")
        print(f"{'='*60}")
        print(f"Base Revenue: ${self.base_revenue:,.0f}")
        print(f"Operating Margin: {self.operating_margin:.1%}")
        print(f"Historical Growth: {self.historical_growth:.1%}")
        print(f"Shares Outstanding: {self.shares_outstanding:,.0f}")
        
        results = {}
        
        for scenario_name in ["conservative", "base", "aggressive"]:
            results[scenario_name] = self.calculate_dcf(scenario_name)
        
        # Summary comparison
        print(f"\n{'='*60}")
        print(f"  VALUATION SUMMARY")
        print(f"{'='*60}")
        
        for scenario_name, result in results.items():
            value = result["value_per_share"]
            print(f"{scenario_name.upper():>15}: ${value:>10,.2f} per share")
        
        # Calculate weighted average (40% base, 30% conservative, 30% aggressive)
        weighted_value = (
            results["base"]["value_per_share"] * 0.40 +
            results["conservative"]["value_per_share"] * 0.30 +
            results["aggressive"]["value_per_share"] * 0.30
        )
        
        print(f"{'WEIGHTED AVG':>15}: ${weighted_value:>10,.2f} per share")
        print(f"{'='*60}\n")
        
        results["weighted_average"] = weighted_value
        results["summary"] = self._build_summary_table(results)
        
        return results
    
    def _build_summary_table(self, results: Dict) -> pd.DataFrame:
        """Build comparison table of all scenarios"""
        summary_data = []
        
        for scenario in ["conservative", "base", "aggressive"]:
            r = results[scenario]
            summary_data.append({
                "Scenario": scenario.capitalize(),
                "Value/Share": r["value_per_share"],
                "Equity Value": r["equity_value"],
                "Enterprise Value": r["enterprise_value"],
                "PV Terminal %": (r["pv_terminal_value"] / r["enterprise_value"] * 100),
                "Discount Rate": r["assumptions"].discount_rate * 100,
                "Terminal Growth": r["assumptions"].terminal_growth_rate * 100
            })
        
        return pd.DataFrame(summary_data)
    
    # ==========================================
    # 5. SENSITIVITY ANALYSIS
    # ==========================================
    
    def sensitivity_analysis(self, 
                            scenario: str = "base",
                            wacc_range: Tuple[float, float] = (0.08, 0.14),
                            growth_range: Tuple[float, float] = (0.01, 0.04),
                            steps: int = 7) -> pd.DataFrame:
        """
        Create sensitivity table varying WACC and terminal growth rate.
        
        Args:
            scenario: Which scenario to use as base
            wacc_range: (min, max) discount rates
            growth_range: (min, max) terminal growth rates
            steps: Number of steps in each dimension
            
        Returns:
            DataFrame with sensitivity matrix
        """
        print(f"\n📈 Generating Sensitivity Analysis for {scenario.upper()}...")
        
        # Get base assumptions
        base_assumptions = self.scenarios[scenario]
        
        # Create ranges
        wacc_values = np.linspace(wacc_range[0], wacc_range[1], steps)
        growth_values = np.linspace(growth_range[0], growth_range[1], steps)
        
        # Build matrix
        matrix = []
        for wacc in wacc_values:
            row = []
            for terminal_growth in growth_values:
                # Create custom assumptions
                custom = DCFAssumptions(
                    revenue_growth_rates=base_assumptions.revenue_growth_rates,
                    terminal_growth_rate=terminal_growth,
                    discount_rate=wacc,
                    tax_rate=base_assumptions.tax_rate,
                    capex_pct_revenue=base_assumptions.capex_pct_revenue,
                    nwc_pct_revenue=base_assumptions.nwc_pct_revenue,
                    depreciation_pct_revenue=base_assumptions.depreciation_pct_revenue,
                    projection_years=base_assumptions.projection_years
                )
                
                # Run DCF
                result = self.calculate_dcf(scenario, custom)
                row.append(result["value_per_share"])
            
            matrix.append(row)
        
        # Convert to DataFrame
        df = pd.DataFrame(
            matrix,
            index=[f"{w:.1%}" for w in wacc_values],
            columns=[f"{g:.1%}" for g in growth_values]
        )
        df.index.name = "WACC ↓"
        df.columns.name = "Terminal Growth →"
        
        print("[OK] Sensitivity Analysis Complete")
        return df


# === CONVENIENCE FUNCTIONS ===

def quick_dcf(ticker: str, financials: Optional[Dict] = None) -> Dict:
    """
    One-line DCF valuation.
    
    Usage:
        results = quick_dcf("AAPL")
        print(f"Fair Value: ${results['base']['value_per_share']:.2f}")
    """
    if financials is None:
        from usa_backend import quick_extract
        financials = quick_extract(ticker)
    
    model = DCFModel(financials)
    return model.run_all_scenarios()


def compare_valuations(tickers: List[str]) -> pd.DataFrame:
    """
    Compare DCF valuations for multiple companies.
    
    Usage:
        comparison = compare_valuations(["AAPL", "MSFT", "GOOGL"])
        print(comparison)
    """
    from usa_backend import quick_extract
    
    results = []
    for ticker in tickers:
        print(f"\n[INFO] Processing {ticker}...")
        try:
            financials = quick_extract(ticker)
            model = DCFModel(financials)
            scenario_results = model.run_all_scenarios()
            
            results.append({
                "Ticker": ticker,
                "Conservative": scenario_results["conservative"]["value_per_share"],
                "Base": scenario_results["base"]["value_per_share"],
                "Aggressive": scenario_results["aggressive"]["value_per_share"],
                "Weighted Avg": scenario_results["weighted_average"]
            })
        except Exception as e:
            print(f"❌ {ticker} failed: {e}")
    
    return pd.DataFrame(results)

