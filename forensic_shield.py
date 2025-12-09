"""
FORENSIC SHIELD: FRAUD & BANKRUPTCY DETECTION
================================================================================
Purpose: Automated forensic accounting screeners
Models: Altman Z-Score, Beneish M-Score, Piotroski F-Score
Author: Atlas Financial Intelligence
Date: November 28, 2025
================================================================================

Theory:
    1. Altman Z-Score: Predicts bankruptcy risk (1968 model, 72-80% accurate)
    2. Beneish M-Score: Detects earnings manipulation (8-variable model)
    3. Piotroski F-Score: Quality score 0-9 (tests fundamental strength)
"""

from typing import Dict, Optional
import pandas as pd


class ForensicShield:
    """
    Forensic Accounting Analysis - Detects fraud, bankruptcy risk, and quality issues
    """
    
    def __init__(self, financials: Dict):
        """
        Initialize with financial data
        
        Args:
            financials: Dictionary from quick_extract
        """
        self.financials = financials
        
        # Extract latest and prior year data
        self.income = financials.get('income_statement')
        self.balance = financials.get('balance_sheet')
        self.cashflow = financials.get('cash_flow')
        
    def _get_metric(self, statement: str, field_names: list, year_idx: int = 0) -> Optional[float]:
        """Extract metric from financial statement"""
        try:
            df = self.financials.get(statement)
            if df is None or df.empty:
                return None
            
            for field in field_names:
                if field in df.index:
                    value = df.loc[field].iloc[year_idx]
                    return float(value) if value is not None else None
            return None
        except:
            return None
    
    def calculate_altman_z_score(self) -> Dict:
        """
        Altman Z-Score: Bankruptcy Prediction Model
        
        Formula (for public manufacturing companies):
            Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5
        
        Where:
            X1 = Working Capital / Total Assets
            X2 = Retained Earnings / Total Assets
            X3 = EBIT / Total Assets
            X4 = Market Value of Equity / Total Liabilities
            X5 = Sales / Total Assets
        
        Interpretation:
            Z > 2.99: Safe Zone (low bankruptcy risk)
            1.81 < Z < 2.99: Grey Zone (moderate risk)
            Z < 1.81: Distress Zone (high bankruptcy risk)
        
        Returns:
            Dictionary with Z-Score, interpretation, and components
        """
        # Get latest year metrics
        total_assets = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'])
        current_assets = self._get_metric('balance_sheet', ['Current Assets', 'Current_Assets'])
        current_liabilities = self._get_metric('balance_sheet', ['Current Liabilities', 'Current_Liabilities'])
        total_liabilities = self._get_metric('balance_sheet', ['Total Liabilities', 'Total_Liabilities', 'Total Liabilities Net Minority Interest'])
        retained_earnings = self._get_metric('balance_sheet', ['Retained Earnings', 'Retained_Earnings'])
        ebit = self._get_metric('income_statement', ['EBIT', 'Operating Income', 'Operating_Income'])
        revenue = self._get_metric('income_statement', ['Total Revenue', 'Total_Revenue'])
        
        # Market value of equity (from market data)
        try:
            shares = self.financials['info'].get('sharesOutstanding', 0)
            price = self.financials['market_data'].get('current_price', 0)
            market_cap = shares * price if shares and price else None
        except:
            market_cap = None
        
        # Check if we have required data
        if not all([total_assets, current_assets, current_liabilities, total_liabilities, ebit, revenue]):
            return {
                'status': 'error',
                'message': 'Insufficient data for Altman Z-Score calculation'
            }
        
        # Calculate components
        working_capital = current_assets - current_liabilities
        x1 = working_capital / total_assets
        x2 = (retained_earnings / total_assets) if retained_earnings else 0
        x3 = ebit / total_assets
        x4 = (market_cap / total_liabilities) if market_cap and total_liabilities > 0 else 0
        x5 = revenue / total_assets
        
        # Calculate Z-Score
        z_score = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (1.0 * x5)
        
        # Interpret
        if z_score > 2.99:
            zone = "Safe Zone"
            risk = "LOW"
            interpretation = "Company appears financially healthy with low bankruptcy risk."
        elif z_score > 1.81:
            zone = "Grey Zone"
            risk = "MODERATE"
            interpretation = "Company shows some financial stress. Monitor closely."
        else:
            zone = "Distress Zone"
            risk = "HIGH"
            interpretation = "Company shows signs of financial distress. High bankruptcy risk!"
        
        return {
            'status': 'success',
            'z_score': z_score,
            'zone': zone,
            'risk_level': risk,
            'interpretation': interpretation,
            'components': {
                'X1_working_capital_to_assets': x1,
                'X2_retained_earnings_to_assets': x2,
                'X3_ebit_to_assets': x3,
                'X4_market_cap_to_liabilities': x4,
                'X5_sales_to_assets': x5
            }
        }
    
    def calculate_beneish_m_score(self) -> Dict:
        """
        Beneish M-Score: Earnings Manipulation Detection
        
        Formula:
            M = -4.84 + 0.92*DSRI + 0.528*GMI + 0.404*AQI + 0.892*SGI +
                0.115*DEPI - 0.172*SGAI + 4.679*TATA - 0.327*LVGI
        
        Where:
            DSRI = Days Sales in Receivables Index
            GMI = Gross Margin Index
            AQI = Asset Quality Index
            SGI = Sales Growth Index
            DEPI = Depreciation Index
            SGAI = Sales, General & Admin Index
            TATA = Total Accruals to Total Assets
            LVGI = Leverage Index
        
        Interpretation:
            M > -1.78: High probability of manipulation
            M < -1.78: Low probability of manipulation
        
        Returns:
            Dictionary with M-Score, interpretation, and warning flags
        """
        # Need current year (t) and prior year (t-1)
        try:
            # Current year (year_idx=0)
            revenue_t = self._get_metric('income_statement', ['Total Revenue', 'Total_Revenue'], 0)
            ar_t = self._get_metric('balance_sheet', ['Accounts Receivable', 'Receivables'], 0)
            cogs_t = self._get_metric('income_statement', ['Cost Of Revenue', 'Cost of Goods Sold', 'COGS'], 0)
            current_assets_t = self._get_metric('balance_sheet', ['Current Assets', 'Current_Assets'], 0)
            ppe_t = self._get_metric('balance_sheet', ['Net PPE', 'Property Plant Equipment Net'], 0)
            total_assets_t = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'], 0)
            depreciation_t = self._get_metric('cash_flow', ['Depreciation', 'Depreciation And Amortization'], 0)
            sga_t = self._get_metric('income_statement', ['Selling General And Administration', 'SG&A'], 0)
            total_debt_t = self._get_metric('balance_sheet', ['Total Debt', 'Long Term Debt'], 0)
            current_liabilities_t = self._get_metric('balance_sheet', ['Current Liabilities', 'Current_Liabilities'], 0)
            net_income_t = self._get_metric('income_statement', ['Net Income', 'Net_Income'], 0)
            cash_flow_ops_t = self._get_metric('cash_flow', ['Operating Cash Flow', 'Total Cash From Operating Activities'], 0)
            
            # Prior year (year_idx=1)
            revenue_t1 = self._get_metric('income_statement', ['Total Revenue', 'Total_Revenue'], 1)
            ar_t1 = self._get_metric('balance_sheet', ['Accounts Receivable', 'Receivables'], 1)
            cogs_t1 = self._get_metric('income_statement', ['Cost Of Revenue', 'Cost of Goods Sold', 'COGS'], 1)
            current_assets_t1 = self._get_metric('balance_sheet', ['Current Assets', 'Current_Assets'], 1)
            current_liabilities_t1 = self._get_metric('balance_sheet', ['Current Liabilities', 'Current_Liabilities'], 1)
            ppe_t1 = self._get_metric('balance_sheet', ['Net PPE', 'Property Plant Equipment Net'], 1)
            total_assets_t1 = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'], 1)
            depreciation_t1 = self._get_metric('cash_flow', ['Depreciation', 'Depreciation And Amortization'], 1)
            sga_t1 = self._get_metric('income_statement', ['Selling General And Administration', 'SG&A'], 1)
            total_debt_t1 = self._get_metric('balance_sheet', ['Total Debt', 'Long Term Debt'], 1)
            
            # Check if we have minimum required data
            if not all([revenue_t, revenue_t1, total_assets_t, net_income_t]):
                return {
                    'status': 'error',
                    'message': 'Insufficient data for Beneish M-Score (need 2 years of data)'
                }
            
            # Calculate indices
            # 1. DSRI = (AR_t / Revenue_t) / (AR_t-1 / Revenue_t-1)
            dsri = ((ar_t / revenue_t) / (ar_t1 / revenue_t1)) if ar_t and ar_t1 and revenue_t1 > 0 else 1.0
            
            # 2. GMI = Gross Margin_t-1 / Gross Margin_t
            gm_t = (revenue_t - (cogs_t or 0)) / revenue_t if revenue_t > 0 else 0
            gm_t1 = (revenue_t1 - (cogs_t1 or 0)) / revenue_t1 if revenue_t1 > 0 and cogs_t1 else 0
            gmi = gm_t1 / gm_t if gm_t > 0 else 1.0
            
            # 3. AQI = [1 - (CA_t + PPE_t) / TA_t] / [1 - (CA_t-1 + PPE_t-1) / TA_t-1]
            aqi_num = 1 - ((current_assets_t or 0) + (ppe_t or 0)) / total_assets_t if total_assets_t > 0 else 0
            aqi_den = 1 - ((current_assets_t1 or 0) + (ppe_t1 or 0)) / total_assets_t1 if total_assets_t1 and total_assets_t1 > 0 else 1
            aqi = aqi_num / aqi_den if aqi_den != 0 else 1.0
            
            # 4. SGI = Revenue_t / Revenue_t-1
            sgi = revenue_t / revenue_t1 if revenue_t1 > 0 else 1.0
            
            # 5. DEPI = (Depreciation_t-1 / (PPE_t-1 + Depreciation_t-1)) / (Depreciation_t / (PPE_t + Depreciation_t))
            depi_num = (depreciation_t1 / ((ppe_t1 or 0) + depreciation_t1)) if depreciation_t1 and ppe_t1 else 0
            depi_den = (depreciation_t / ((ppe_t or 0) + depreciation_t)) if depreciation_t and ppe_t else 1
            depi = depi_num / depi_den if depi_den != 0 else 1.0
            
            # 6. SGAI = (SGA_t / Revenue_t) / (SGA_t-1 / Revenue_t-1)
            sgai = ((sga_t or 0) / revenue_t) / ((sga_t1 or 0) / revenue_t1) if sga_t and sga_t1 and revenue_t1 > 0 else 1.0
            
            # 7. LVGI = Total Debt_t / Total Debt_t-1
            lvgi = (total_debt_t / total_debt_t1) if total_debt_t and total_debt_t1 and total_debt_t1 > 0 else 1.0
            
            # 8. TATA = (Change in Working Capital - Cash Flow from Operations) / Total Assets
            wc_t = ((current_assets_t or 0) - (current_liabilities_t or 0))
            wc_t1 = ((current_assets_t1 or 0) - (current_liabilities_t1 or 0)) if current_assets_t1 is not None and current_liabilities_t1 is not None else 0
            working_capital_change = wc_t - wc_t1
            tata = (working_capital_change - (cash_flow_ops_t or 0)) / total_assets_t if total_assets_t and total_assets_t > 0 else 0
            
            # Calculate M-Score
            m_score = (-4.84 + 
                       0.92 * dsri + 
                       0.528 * gmi + 
                       0.404 * aqi + 
                       0.892 * sgi + 
                       0.115 * depi - 
                       0.172 * sgai + 
                       4.679 * tata - 
                       0.327 * lvgi)
            
            # Interpret
            if m_score > -1.78:
                risk = "HIGH"
                interpretation = "HIGH PROBABILITY OF EARNINGS MANIPULATION! Red flag detected."
                warning = "CAUTION: Financial statements may be manipulated."
            else:
                risk = "LOW"
                interpretation = "Low probability of earnings manipulation. Financial statements appear reliable."
                warning = None
            
            # Red flags
            red_flags = []
            if dsri > 1.031: red_flags.append("Receivables growing faster than sales")
            if gmi > 1.014: red_flags.append("Gross margin deteriorating")
            if aqi > 1.039: red_flags.append("Asset quality declining")
            if sgi > 1.607: red_flags.append("Sales growth unusually high")
            if tata > 0.031: red_flags.append("High accruals (earnings vs. cash divergence)")
            
            return {
                'status': 'success',
                'm_score': m_score,
                'risk_level': risk,
                'interpretation': interpretation,
                'warning': warning,
                'red_flags': red_flags if red_flags else None,
                'components': {
                    'DSRI': dsri,
                    'GMI': gmi,
                    'AQI': aqi,
                    'SGI': sgi,
                    'DEPI': depi,
                    'SGAI': sgai,
                    'TATA': tata,
                    'LVGI': lvgi
                }
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Beneish M-Score calculation error: {e}'
            }
    
    def calculate_piotroski_f_score(self) -> Dict:
        """
        Piotroski F-Score: 9-Point Quality Test
        
        Tests 3 categories:
            1. Profitability (4 points)
            2. Leverage/Liquidity (3 points)
            3. Operating Efficiency (2 points)
        
        Score:
            8-9: High quality, strong fundamentals
            5-7: Average quality
            0-4: Low quality, weak fundamentals
        
        Returns:
            Dictionary with F-Score (0-9), breakdown, and interpretation
        """
        score = 0
        breakdown = {}
        
        # Get metrics
        net_income_t = self._get_metric('income_statement', ['Net Income', 'Net_Income'], 0)
        total_assets_t0 = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'], 0)
        roa_t = (net_income_t / total_assets_t0) if net_income_t and total_assets_t0 and total_assets_t0 > 0 else 0
        cf_ops_t = self._get_metric('cash_flow', ['Operating Cash Flow', 'Total Cash From Operating Activities'], 0)
        
        net_income_t1 = self._get_metric('income_statement', ['Net Income', 'Net_Income'], 1)
        total_assets_t0_for_roa = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'], 1)
        roa_t1 = (net_income_t1 / total_assets_t0_for_roa) if net_income_t1 and total_assets_t0_for_roa and total_assets_t0_for_roa > 0 else 0
        
        current_assets_t = self._get_metric('balance_sheet', ['Current Assets', 'Current_Assets'], 0)
        current_liabilities_t = self._get_metric('balance_sheet', ['Current Liabilities', 'Current_Liabilities'], 0)
        
        total_assets_t = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'], 0)
        total_assets_t1 = self._get_metric('balance_sheet', ['Total Assets', 'Total_Assets'], 1)
        
        shares_t = self._get_metric('balance_sheet', ['Share Issued', 'Ordinary Shares Number'], 0)
        shares_t1 = self._get_metric('balance_sheet', ['Share Issued', 'Ordinary Shares Number'], 1)
        
        revenue_t = self._get_metric('income_statement', ['Total Revenue', 'Total_Revenue'], 0)
        revenue_t1 = self._get_metric('income_statement', ['Total Revenue', 'Total_Revenue'], 1)
        
        # 1. PROFITABILITY TESTS (4 points)
        # 1a. Positive net income
        if net_income_t and net_income_t > 0:
            score += 1
            breakdown['positive_net_income'] = 1
        else:
            breakdown['positive_net_income'] = 0
        
        # 1b. Positive operating cash flow
        if cf_ops_t and cf_ops_t > 0:
            score += 1
            breakdown['positive_cash_flow'] = 1
        else:
            breakdown['positive_cash_flow'] = 0
        
        # 1c. ROA increase year-over-year
        if roa_t and roa_t1 and roa_t > roa_t1:
            score += 1
            breakdown['roa_increasing'] = 1
        else:
            breakdown['roa_increasing'] = 0
        
        # 1d. Quality of earnings (OCF > Net Income)
        if cf_ops_t and net_income_t and cf_ops_t > net_income_t:
            score += 1
            breakdown['quality_of_earnings'] = 1
        else:
            breakdown['quality_of_earnings'] = 0
        
        # 2. LEVERAGE/LIQUIDITY TESTS (3 points)
        # 2a. Long-term debt decreased
        debt_t = self._get_metric('balance_sheet', ['Long Term Debt', 'Total Debt'], 0)
        debt_t1 = self._get_metric('balance_sheet', ['Long Term Debt', 'Total Debt'], 1)
        if debt_t is not None and debt_t1 is not None and debt_t < debt_t1:
            score += 1
            breakdown['debt_decreasing'] = 1
        else:
            breakdown['debt_decreasing'] = 0
        
        # 2b. Current ratio increased
        current_ratio_t = current_assets_t / current_liabilities_t if current_assets_t and current_liabilities_t and current_liabilities_t > 0 else 0
        current_assets_t1 = self._get_metric('balance_sheet', ['Current Assets', 'Current_Assets'], 1)
        current_liabilities_t1 = self._get_metric('balance_sheet', ['Current Liabilities', 'Current_Liabilities'], 1)
        current_ratio_t1 = current_assets_t1 / current_liabilities_t1 if current_assets_t1 and current_liabilities_t1 and current_liabilities_t1 > 0 else 0
        
        if current_ratio_t and current_ratio_t1 and current_ratio_t > current_ratio_t1:
            score += 1
            breakdown['current_ratio_increasing'] = 1
        else:
            breakdown['current_ratio_increasing'] = 0
        
        # 2c. No new shares issued (shares outstanding didn't increase)
        if shares_t is not None and shares_t1 is not None and shares_t <= shares_t1:
            score += 1
            breakdown['no_share_dilution'] = 1
        else:
            breakdown['no_share_dilution'] = 0
        
        # 3. OPERATING EFFICIENCY TESTS (2 points)
        # 3a. Gross margin increased
        cogs_t = self._get_metric('income_statement', ['Cost Of Revenue', 'COGS'], 0)
        cogs_t1 = self._get_metric('income_statement', ['Cost Of Revenue', 'COGS'], 1)
        gross_margin_t = (revenue_t - (cogs_t or 0)) / revenue_t if revenue_t and revenue_t > 0 else 0
        gross_margin_t1 = (revenue_t1 - (cogs_t1 or 0)) / revenue_t1 if revenue_t1 and revenue_t1 > 0 else 0
        
        if gross_margin_t and gross_margin_t1 and gross_margin_t > gross_margin_t1:
            score += 1
            breakdown['gross_margin_increasing'] = 1
        else:
            breakdown['gross_margin_increasing'] = 0
        
        # 3b. Asset turnover increased
        asset_turnover_t = revenue_t / total_assets_t if revenue_t and total_assets_t and total_assets_t > 0 else 0
        asset_turnover_t1 = revenue_t1 / total_assets_t1 if revenue_t1 and total_assets_t1 and total_assets_t1 > 0 else 0
        
        if asset_turnover_t and asset_turnover_t1 and asset_turnover_t > asset_turnover_t1:
            score += 1
            breakdown['asset_turnover_increasing'] = 1
        else:
            breakdown['asset_turnover_increasing'] = 0
        
        # Interpret
        if score >= 8:
            quality = "High Quality"
            interpretation = "Strong fundamentals. Company shows excellent financial health."
        elif score >= 5:
            quality = "Average Quality"
            interpretation = "Moderate fundamentals. Some strengths, some weaknesses."
        else:
            quality = "Low Quality"
            interpretation = "Weak fundamentals. Company shows financial deterioration."
        
        return {
            'status': 'success',
            'f_score': score,
            'max_score': 9,
            'quality': quality,
            'interpretation': interpretation,
            'breakdown': breakdown
        }
    
    def run_full_forensic_analysis(self) -> Dict:
        """
        Run all 3 forensic tests
        
        Returns:
            Dictionary with results from all 3 models
        """
        return {
            'altman_z_score': self.calculate_altman_z_score(),
            'beneish_m_score': self.calculate_beneish_m_score(),
            'piotroski_f_score': self.calculate_piotroski_f_score()
        }


def analyze_forensic_shield(financials: Dict) -> Dict:
    """
    Main function to run forensic analysis
    
    Returns:
        Dictionary with all 3 forensic scores and overall risk assessment
    """
    shield = ForensicShield(financials)
    results = shield.run_full_forensic_analysis()
    
    # Overall risk assessment
    risk_factors = []
    
    if results['altman_z_score']['status'] == 'success':
        if results['altman_z_score']['risk_level'] == 'HIGH':
            risk_factors.append('High bankruptcy risk (Altman Z-Score)')
    
    if results['beneish_m_score']['status'] == 'success':
        if results['beneish_m_score']['risk_level'] == 'HIGH':
            risk_factors.append('High manipulation risk (Beneish M-Score)')
    
    if results['piotroski_f_score']['status'] == 'success':
        if results['piotroski_f_score']['f_score'] < 5:
            risk_factors.append('Low quality fundamentals (Piotroski F-Score)')
    
    overall_risk = "HIGH" if len(risk_factors) >= 2 else "MODERATE" if len(risk_factors) == 1 else "LOW"
    
    results['overall_assessment'] = {
        'risk_level': overall_risk,
        'risk_factors': risk_factors if risk_factors else None,
        'summary': f"Overall Risk: {overall_risk}. {len(risk_factors)} red flag(s) detected." if risk_factors else "No major red flags detected. Company appears financially sound."
    }
    
    return results

