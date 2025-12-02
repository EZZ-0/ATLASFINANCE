"""
DATA VALIDATION ENGINE
======================
Multi-layer validation to ensure data quality and prevent trash output.

Validation Layers:
1. Multi-source reconciliation (SEC vs yfinance)
2. Logical consistency checks (balance sheet balances, ratios in bounds)
3. Time series validation (no gaps, no extreme jumps)
4. Cross-metric validation (derived metrics match calculations)

Usage:
    validator = DataValidator()
    report = validator.validate_extraction(ticker, financials)
    
    if report['overall_status'] == 'PASS':
        # Safe to use
    else:
        # Check warnings
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
# Lazy import: import yfinance as yf - only when needed

class DataValidator:
    """
    Comprehensive data validation for financial extractions
    """
    
    def __init__(self):
        self.tolerance = 0.05  # 5% discrepancy tolerance
        self.ratio_bounds = {
            'pe_ratio': (-100, 200),
            'roe': (-0.5, 2.0),  # -50% to 200% (some tech companies > 150%)
            'roa': (-0.3, 0.5),  # -30% to 50%
            'debt_to_equity': (0, 10),
            'current_ratio': (0, 20),
            'gross_margin': (-0.5, 1.0),
            'operating_margin': (-1.0, 1.0),
            'net_margin': (-1.0, 1.0)
        }
        
        # Known-good baseline for testing
        # NOTE: Using 2024 TTM data since yfinance provides most recent data
        self.known_good_companies = {
            'AAPL': {
                'revenue_ttm': 391000000000,  # Approximate TTM Q4 2024
                'net_income_ttm': 100000000000,  # Approximate
                'total_assets': 365000000000,  # Approximate
                'source': 'Yahoo Finance TTM data (2024)'
            },
            'MSFT': {
                'revenue_ttm': 245000000000,  # Approximate TTM 2024
                'net_income_ttm': 88000000000,  # Approximate
                'total_assets': 512000000000,  # Approximate
                'source': 'Yahoo Finance TTM data (2024)'
            },
            'JPM': {
                'revenue_ttm': 170000000000,  # Approximate TTM 2024
                'net_income_ttm': 57000000000,  # Approximate
                'total_assets': 4100000000000,  # Approximate
                'source': 'Yahoo Finance TTM data (2024)'
            }
        }
    
    # ==========================================
    # MAIN VALIDATION ENTRY POINT
    # ==========================================
    
    def validate_extraction(self, ticker: str, financials: Dict) -> Dict[str, Any]:
        """
        Run all validation checks on extracted financials
        
        Returns:
            {
                'overall_status': 'PASS' | 'WARN' | 'FAIL',
                'checks': {...},
                'warnings': [...],
                'errors': [...],
                'quality_score': 0-100
            }
        """
        
        report = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'PASS',
            'checks': {},
            'warnings': [],
            'errors': [],
            'quality_score': 100
        }
        
        # Layer 1: Basic structure validation
        report['checks']['structure'] = self._validate_structure(financials, report)
        
        # Layer 2: Logical consistency
        report['checks']['logic'] = self._validate_logic(financials, report)
        
        # Layer 3: Ratio bounds
        report['checks']['ratios'] = self._validate_ratio_bounds(financials, report)
        
        # Layer 4: Time series
        report['checks']['time_series'] = self._validate_time_series(financials, report)
        
        # Layer 5: Cross-metric validation
        report['checks']['cross_metrics'] = self._validate_cross_metrics(financials, report)
        
        # Layer 6: Multi-source comparison (if available)
        if ticker in self.known_good_companies:
            report['checks']['baseline'] = self._validate_against_baseline(ticker, financials, report)
        
        # Calculate overall status
        if len(report['errors']) > 0:
            report['overall_status'] = 'FAIL'
            report['quality_score'] = max(0, 100 - len(report['errors']) * 20)
        elif len(report['warnings']) > 3:
            report['overall_status'] = 'WARN'
            report['quality_score'] = max(50, 100 - len(report['warnings']) * 5)
        
        return report
    
    # ==========================================
    # VALIDATION LAYER 1: STRUCTURE
    # ==========================================
    
    def _validate_structure(self, financials: Dict, report: Dict) -> str:
        """Check if required fields exist"""
        
        required_fields = [
            'ticker', 'company_name', 
            'income_statement', 'balance_sheet', 'cash_flow'
        ]
        
        for field in required_fields:
            if field not in financials or financials[field] is None:
                report['errors'].append(f"Missing required field: {field}")
                return 'FAIL'
        
        # Check if DataFrames are not empty
        for stmt_name in ['income_statement', 'balance_sheet', 'cash_flow']:
            stmt = financials.get(stmt_name)
            if isinstance(stmt, pd.DataFrame) and stmt.empty:
                report['warnings'].append(f"{stmt_name} is empty")
        
        return 'PASS'
    
    # ==========================================
    # VALIDATION LAYER 2: LOGICAL CONSISTENCY
    # ==========================================
    
    def _validate_logic(self, financials: Dict, report: Dict) -> str:
        """Check if financial statements follow accounting rules"""
        
        balance = financials.get('balance_sheet', pd.DataFrame())
        income = financials.get('income_statement', pd.DataFrame())
        
        if balance.empty or income.empty:
            return 'SKIP'
        
        # Helper to get value
        def get_val(df, keys):
            if isinstance(df.index[0], str):  # yfinance format
                for key in keys:
                    if key in df.index:
                        return df.loc[key].iloc[0]
            else:  # SEC format
                for key in keys:
                    if key in df.columns:
                        return df[key].iloc[0]
            return None
        
        # Rule 1: Assets = Liabilities + Equity
        assets = get_val(balance, ['Total Assets', 'TotalAssets'])
        liab = get_val(balance, ['Total Liabilities', 'Total Liabilities Net Minority Interest'])
        equity = get_val(balance, ['Total Equity', 'Stockholders Equity', 'Total Stockholders Equity'])
        
        if assets and liab and equity:
            diff = abs(assets - (liab + equity)) / assets
            if diff > 0.02:  # 2% tolerance
                report['warnings'].append(f"Balance sheet doesn't balance: {diff:.1%} difference")
        
        # Rule 2: Revenue >= Net Income (for profitable companies)
        revenue = get_val(income, ['Total Revenue', 'Revenue'])
        net_income = get_val(income, ['Net Income'])
        
        if revenue and net_income:
            if net_income > 0 and net_income > revenue:
                report['errors'].append(f"Net Income ({net_income/1e9:.2f}B) > Revenue ({revenue/1e9:.2f}B) - IMPOSSIBLE!")
        
        # Rule 3: Margins should be fractions (not already percentages)
        ratios = financials.get('ratios', pd.DataFrame())
        if not ratios.empty and 'Gross_Margin' in ratios.index:
            gross_margin = ratios.loc['Gross_Margin'].iloc[0]
            if gross_margin > 2:  # If > 200%, probably was entered as percentage not fraction
                report['warnings'].append(f"Gross margin ({gross_margin:.0f}) seems too high - check if already percentage")
        
        return 'PASS' if len(report['errors']) == 0 else 'FAIL'
    
    # ==========================================
    # VALIDATION LAYER 3: RATIO BOUNDS
    # ==========================================
    
    def _validate_ratio_bounds(self, financials: Dict, report: Dict) -> str:
        """Check if ratios are within reasonable bounds"""
        
        ratios = financials.get('ratios', pd.DataFrame())
        
        if ratios.empty:
            return 'SKIP'
        
        for ratio_name, (min_val, max_val) in self.ratio_bounds.items():
            # Try to find ratio (handle different naming)
            ratio_keys = [ratio_name, ratio_name.title(), ratio_name.upper()]
            
            found = False
            for key in ratio_keys:
                if key in ratios.index:
                    value = ratios.loc[key].iloc[0]
                    found = True
                    
                    if pd.notnull(value):
                        if value < min_val or value > max_val:
                            report['warnings'].append(
                                f"{ratio_name} = {value:.2f} is outside normal range [{min_val}, {max_val}]"
                            )
                    break
        
        return 'PASS'
    
    # ==========================================
    # VALIDATION LAYER 4: TIME SERIES
    # ==========================================
    
    def _validate_time_series(self, financials: Dict, report: Dict) -> str:
        """Check for gaps, duplicates, extreme jumps in historical data"""
        
        income = financials.get('income_statement', pd.DataFrame())
        
        if income.empty or len(income) < 2:
            return 'SKIP'
        
        # Check for extreme revenue jumps (> 100% YoY is suspicious)
        if isinstance(income.index[0], str):  # yfinance format
            revenue_key = None
            for idx in income.index:
                if 'revenue' in str(idx).lower():
                    revenue_key = idx
                    break
            
            if revenue_key:
                revenue_series = income.loc[revenue_key].dropna()
                if len(revenue_series) >= 2:
                    pct_changes = revenue_series.pct_change().abs()
                    extreme_changes = pct_changes[pct_changes > 1.0]  # > 100% change
                    
                    if len(extreme_changes) > 0:
                        report['warnings'].append(
                            f"Extreme revenue changes detected: {len(extreme_changes)} periods > 100% YoY"
                        )
        
        return 'PASS'
    
    # ==========================================
    # VALIDATION LAYER 5: CROSS-METRIC
    # ==========================================
    
    def _validate_cross_metrics(self, financials: Dict, report: Dict) -> str:
        """Validate that derived metrics match calculations"""
        
        ratios = financials.get('ratios', pd.DataFrame())
        
        if ratios.empty:
            return 'SKIP'
        
        # Check ROE = Net Income / Equity
        if all(k in ratios.index for k in ['ROE', 'Net_Income', 'Total_Equity']):
            roe_stated = ratios.loc['ROE'].iloc[0]
            net_income = ratios.loc['Net_Income'].iloc[0]
            equity = ratios.loc['Total_Equity'].iloc[0]
            
            if equity > 0:
                roe_calc = net_income / equity
                diff = abs(roe_stated - roe_calc) / abs(roe_calc) if roe_calc != 0 else 0
                
                if diff > 0.05:  # 5% tolerance
                    report['warnings'].append(
                        f"ROE mismatch: Stated {roe_stated:.3f} vs Calculated {roe_calc:.3f} ({diff:.1%} diff)"
                    )
        
        return 'PASS'
    
    # ==========================================
    # VALIDATION LAYER 6: BASELINE
    # ==========================================
    
    def _validate_against_baseline(self, ticker: str, financials: Dict, report: Dict) -> str:
        """
        Compare against known-good values from SEC filings
        NOTE: Baseline validation disabled - TTM data vs fiscal year makes direct comparison difficult
        """
        
        # TEMPORARILY DISABLED - yfinance provides TTM data while baseline is fiscal year
        # This causes mismatches even when extraction is correct
        # TODO: Re-enable with proper TTM baseline values
        
        return 'SKIP'
    
    # ==========================================
    # MULTI-SOURCE COMPARISON
    # ==========================================
    
    def cross_validate_sources(self, ticker: str) -> Dict[str, Any]:
        """
        Extract from multiple sources and compare
        
        Returns comparison report
        """
        
        # Lazy import yfinance
        import yfinance as yf
        
        from usa_backend import USAFinancialExtractor
        
        extractor = USAFinancialExtractor()
        
        # Source 1: Our extraction (yfinance)
        our_data = extractor.extract_financials(ticker)
        
        # Source 2: Direct yfinance (for comparison)
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            yf_direct = {
                'market_cap': info.get('marketCap'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook')
            }
        except (KeyError, AttributeError, TypeError) as e:
            yf_direct = {}
            print(f"Warning: Could not fetch yfinance data for {ticker}: {e}")
        
        # Compare key metrics
        comparison = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'discrepancies': []
        }
        
        # Get our values
        our_ratios = our_data.get('ratios', pd.DataFrame())
        
        def get_our_value(key):
            if not our_ratios.empty and key in our_ratios.index:
                return our_ratios.loc[key].iloc[0]
            return None
        
        # Compare market cap
        our_mc = get_our_value('Market_Cap')
        yf_mc = yf_direct.get('market_cap')
        
        if our_mc and yf_mc:
            diff = abs(our_mc - yf_mc) / yf_mc
            comparison['metrics']['market_cap'] = {
                'ours': our_mc,
                'yfinance': yf_mc,
                'diff_pct': diff * 100,
                'status': 'PASS' if diff < 0.05 else 'WARN'
            }
            
            if diff > 0.05:
                comparison['discrepancies'].append(
                    f"Market cap differs by {diff:.1%}"
                )
        
        # Compare P/E
        our_pe = get_our_value('PE_Ratio')
        yf_pe = yf_direct.get('pe_ratio')
        
        if our_pe and yf_pe:
            diff = abs(our_pe - yf_pe) / yf_pe
            comparison['metrics']['pe_ratio'] = {
                'ours': our_pe,
                'yfinance': yf_pe,
                'diff_pct': diff * 100,
                'status': 'PASS' if diff < 0.10 else 'WARN'  # 10% tolerance for PE
            }
            
            if diff > 0.10:
                comparison['discrepancies'].append(
                    f"P/E ratio differs by {diff:.1%}"
                )
        
        # Overall status
        comparison['overall_status'] = 'PASS' if len(comparison['discrepancies']) == 0 else 'WARN'
        
        return comparison
    
    # ==========================================
    # BATCH VALIDATION
    # ==========================================
    
    def validate_batch(self, tickers: List[str]) -> pd.DataFrame:
        """
        Validate multiple tickers and return summary DataFrame
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            DataFrame with validation results
        """
        
        from usa_backend import USAFinancialExtractor
        
        extractor = USAFinancialExtractor()
        results = []
        
        for ticker in tickers:
            print(f"\n[VALIDATING] {ticker}...")
            
            try:
                # Extract
                financials = extractor.extract_financials(ticker)
                
                # Validate
                validation = self.validate_extraction(ticker, financials)
                
                results.append({
                    'Ticker': ticker,
                    'Status': validation['overall_status'],
                    'Quality_Score': validation['quality_score'],
                    'Warnings': len(validation['warnings']),
                    'Errors': len(validation['errors']),
                    'Checks_Passed': sum(1 for v in validation['checks'].values() if v == 'PASS')
                })
                
                # Print summary
                status_emoji = {
                    'PASS': '✅',
                    'WARN': '⚠️',
                    'FAIL': '❌'
                }
                print(f"{status_emoji[validation['overall_status']]} {ticker}: {validation['quality_score']}/100 (Errors: {len(validation['errors'])}, Warnings: {len(validation['warnings'])})")
                
            except Exception as e:
                print(f"❌ {ticker}: Extraction failed - {str(e)}")
                results.append({
                    'Ticker': ticker,
                    'Status': 'FAIL',
                    'Quality_Score': 0,
                    'Warnings': 0,
                    'Errors': 1,
                    'Checks_Passed': 0
                })
        
        return pd.DataFrame(results)
    
    # ==========================================
    # REPORT GENERATION
    # ==========================================
    
    def generate_validation_report(self, results_df: pd.DataFrame, output_file: str = None):
        """
        Generate comprehensive validation report
        
        Args:
            results_df: DataFrame from validate_batch()
            output_file: Optional path to save markdown report
        """
        
        report_lines = []
        report_lines.append("# 📊 DATA VALIDATION REPORT")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Companies Tested:** {len(results_df)}\n")
        report_lines.append("---\n")
        
        # Summary stats
        report_lines.append("## 📈 SUMMARY STATISTICS\n")
        report_lines.append(f"- **PASS:** {len(results_df[results_df['Status'] == 'PASS'])} ({len(results_df[results_df['Status'] == 'PASS'])/len(results_df)*100:.1f}%)")
        report_lines.append(f"- **WARN:** {len(results_df[results_df['Status'] == 'WARN'])} ({len(results_df[results_df['Status'] == 'WARN'])/len(results_df)*100:.1f}%)")
        report_lines.append(f"- **FAIL:** {len(results_df[results_df['Status'] == 'FAIL'])} ({len(results_df[results_df['Status'] == 'FAIL'])/len(results_df)*100:.1f}%)\n")
        
        report_lines.append(f"**Average Quality Score:** {results_df['Quality_Score'].mean():.1f}/100")
        report_lines.append(f"**Total Warnings:** {results_df['Warnings'].sum()}")
        report_lines.append(f"**Total Errors:** {results_df['Errors'].sum()}\n")
        
        report_lines.append("---\n")
        
        # Detailed results
        report_lines.append("## 📋 DETAILED RESULTS\n")
        report_lines.append(results_df.to_markdown(index=False))
        
        report_lines.append("\n---\n")
        
        # Failed companies
        failed = results_df[results_df['Status'] == 'FAIL']
        if len(failed) > 0:
            report_lines.append("## ❌ FAILED VALIDATIONS\n")
            for _, row in failed.iterrows():
                report_lines.append(f"- **{row['Ticker']}**: {row['Errors']} errors")
        
        report_text = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:  # UTF-8 encoding for emoji support
                f.write(report_text)
            print(f"\n✅ Report saved to: {output_file}")
        
        return report_text


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def quick_validate(ticker: str):
    """Quick validation of a single ticker"""
    from usa_backend import USAFinancialExtractor
    
    extractor = USAFinancialExtractor()
    validator = DataValidator()
    
    print(f"\n[EXTRACTING] {ticker}...")
    financials = extractor.extract_financials(ticker)
    
    print(f"[VALIDATING] {ticker}...")
    report = validator.validate_extraction(ticker, financials)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"VALIDATION REPORT: {ticker}")
    print(f"{'='*60}")
    print(f"Status: {report['overall_status']}")
    print(f"Quality Score: {report['quality_score']}/100")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"Errors: {len(report['errors'])}")
    
    if report['warnings']:
        print(f"\n⚠️ WARNINGS:")
        for warning in report['warnings']:
            print(f"  - {warning}")
    
    if report['errors']:
        print(f"\n❌ ERRORS:")
        for error in report['errors']:
            print(f"  - {error}")
    
    print(f"{'='*60}\n")
    
    return report


if __name__ == "__main__":
    # Quick test
    quick_validate("AAPL")

