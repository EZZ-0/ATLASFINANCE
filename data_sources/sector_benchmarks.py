"""
Sector Benchmarks Integration for ATLAS Financial Intelligence
================================================================

Integrates Damodaran industry data with ATLAS to provide:
- Industry comparison for metrics
- Percentile rankings
- Above/Below industry indicators
- Benchmark context for valuation

Author: ATLAS Financial Intelligence
Created: 2025-12-07 (TASK-A005)
"""

from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import logging

# Import Damodaran data
from data_sources.damodaran_data import (
    get_damodaran_client,
    GICS_TO_DAMODARAN
)

logger = logging.getLogger(__name__)


class ComparisonStatus(Enum):
    """Status relative to industry benchmark."""
    BELOW = "below"
    AT = "at"
    ABOVE = "above"
    UNKNOWN = "unknown"


@dataclass
class BenchmarkComparison:
    """Result of comparing a metric against industry benchmark."""
    metric_name: str
    company_value: float
    industry_value: Optional[float]
    industry_name: str
    status: ComparisonStatus
    difference_percent: Optional[float]
    is_better: Optional[bool]  # True if company outperforms (context-aware)
    interpretation: str


class SectorBenchmarks:
    """
    Provides sector/industry benchmarks for company metrics.
    
    Usage:
        benchmarks = SectorBenchmarks()
        
        # Get all benchmarks for a company
        result = benchmarks.get_benchmarks_for_company(
            sector="Technology",
            industry="Software",
            company_metrics={
                'pe_ratio': 28.5,
                'roe': 0.45,
                'operating_margin': 0.35
            }
        )
        
        # Compare single metric
        comparison = benchmarks.compare_metric(
            metric='pe_ratio',
            company_value=28.5,
            sector='Technology'
        )
    """
    
    # Define which metrics "higher is better" vs "lower is better"
    METRIC_DIRECTIONS = {
        # Higher is better
        'roe': 'higher',
        'roa': 'higher',
        'roic': 'higher',
        'gross_margin': 'higher',
        'operating_margin': 'higher',
        'net_margin': 'higher',
        
        # Lower is better
        'pe_ratio': 'lower',
        'ev_ebitda': 'lower',
        'debt_equity': 'lower',
        'd_e_ratio': 'lower',
        'wacc': 'lower',
        'cost_of_equity': 'lower',
        'cost_of_debt': 'lower',
        
        # Neutral (closer to 1.0 is often "normal")
        'beta': 'neutral',
        'unlevered_beta': 'neutral',
        'levered_beta': 'neutral'
    }
    
    # Metric display names
    METRIC_NAMES = {
        'pe_ratio': 'P/E Ratio',
        'roe': 'Return on Equity',
        'roa': 'Return on Assets',
        'roic': 'Return on Invested Capital',
        'gross_margin': 'Gross Margin',
        'operating_margin': 'Operating Margin',
        'net_margin': 'Net Margin',
        'ev_ebitda': 'EV/EBITDA',
        'debt_equity': 'Debt/Equity',
        'd_e_ratio': 'Debt/Equity',
        'wacc': 'WACC',
        'cost_of_equity': 'Cost of Equity',
        'cost_of_debt': 'Cost of Debt',
        'beta': 'Beta',
        'unlevered_beta': 'Unlevered Beta',
        'levered_beta': 'Levered Beta'
    }
    
    def __init__(self):
        """Initialize sector benchmarks."""
        self.damodaran = get_damodaran_client()
    
    def get_industry_name(self, sector: str, industry: Optional[str] = None) -> str:
        """
        Get Damodaran industry name from GICS sector/industry.
        
        Args:
            sector: GICS sector (e.g., "Technology")
            industry: Optional GICS industry (e.g., "Software")
            
        Returns:
            Damodaran industry name
        """
        # Try industry first (more specific)
        if industry:
            damodaran_name = GICS_TO_DAMODARAN.get(industry)
            if damodaran_name:
                return damodaran_name
        
        # Fall back to sector
        damodaran_name = GICS_TO_DAMODARAN.get(sector)
        if damodaran_name:
            return damodaran_name
        
        # Return as-is (might still work with fuzzy matching)
        return industry if industry else sector
    
    def compare_metric(
        self,
        metric: str,
        company_value: float,
        sector: str,
        industry: Optional[str] = None
    ) -> BenchmarkComparison:
        """
        Compare a single metric against industry benchmark.
        
        Args:
            metric: Metric name (e.g., 'pe_ratio', 'roe')
            company_value: Company's value for the metric
            sector: GICS sector
            industry: Optional GICS industry
            
        Returns:
            BenchmarkComparison with all details
        """
        industry_name = self.get_industry_name(sector, industry)
        benchmarks = self.damodaran.get_all_benchmarks(industry_name)
        
        # Find the industry value for this metric
        industry_value = self._find_metric_in_benchmarks(metric, benchmarks)
        
        if industry_value is None:
            return BenchmarkComparison(
                metric_name=self.METRIC_NAMES.get(metric, metric),
                company_value=company_value,
                industry_value=None,
                industry_name=industry_name,
                status=ComparisonStatus.UNKNOWN,
                difference_percent=None,
                is_better=None,
                interpretation=f"No industry benchmark available for {metric}"
            )
        
        # Calculate difference
        if industry_value != 0:
            diff_percent = ((company_value - industry_value) / abs(industry_value)) * 100
        else:
            diff_percent = 100 if company_value > 0 else (-100 if company_value < 0 else 0)
        
        # Determine status
        if abs(diff_percent) < 5:
            status = ComparisonStatus.AT
        elif diff_percent > 0:
            status = ComparisonStatus.ABOVE
        else:
            status = ComparisonStatus.BELOW
        
        # Determine if better (context-aware)
        direction = self.METRIC_DIRECTIONS.get(metric, 'neutral')
        if direction == 'higher':
            is_better = company_value > industry_value
        elif direction == 'lower':
            is_better = company_value < industry_value
        else:
            is_better = None  # Neutral metrics
        
        # Generate interpretation
        interpretation = self._generate_interpretation(
            metric, company_value, industry_value, diff_percent, is_better, industry_name
        )
        
        return BenchmarkComparison(
            metric_name=self.METRIC_NAMES.get(metric, metric),
            company_value=company_value,
            industry_value=industry_value,
            industry_name=industry_name,
            status=status,
            difference_percent=diff_percent,
            is_better=is_better,
            interpretation=interpretation
        )
    
    def get_benchmarks_for_company(
        self,
        sector: str,
        industry: Optional[str] = None,
        company_metrics: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Get all benchmarks for a company with optional comparison.
        
        Args:
            sector: GICS sector
            industry: Optional GICS industry
            company_metrics: Optional dict of company metrics to compare
            
        Returns:
            Dict with industry benchmarks and comparisons
        """
        industry_name = self.get_industry_name(sector, industry)
        benchmarks = self.damodaran.get_all_benchmarks(industry_name)
        
        result = {
            'industry': industry_name,
            'sector': sector,
            'benchmarks': benchmarks,
            'comparisons': {}
        }
        
        if company_metrics:
            for metric, value in company_metrics.items():
                if value is not None:
                    comparison = self.compare_metric(metric, value, sector, industry)
                    result['comparisons'][metric] = {
                        'company': value,
                        'industry': comparison.industry_value,
                        'status': comparison.status.value,
                        'diff_percent': comparison.difference_percent,
                        'is_better': comparison.is_better,
                        'interpretation': comparison.interpretation
                    }
        
        return result
    
    def get_valuation_context(
        self,
        sector: str,
        company_pe: Optional[float] = None,
        company_ev_ebitda: Optional[float] = None,
        company_pb: Optional[float] = None,
        industry: Optional[str] = None
    ) -> Dict:
        """
        Get valuation context for DCF/multiple analysis.
        
        Returns industry P/E, EV/EBITDA for context in valuation.
        """
        industry_name = self.get_industry_name(sector, industry)
        benchmarks = self.damodaran.get_all_benchmarks(industry_name)
        
        multiples = benchmarks.get('multiples', {})
        
        result = {
            'industry': industry_name,
            'industry_pe': multiples.get('pe_ratio'),
            'industry_ev_ebitda': multiples.get('ev_ebitda'),
            'industry_peg': multiples.get('peg_ratio'),
        }
        
        # Add comparisons if company values provided
        if company_pe and result['industry_pe']:
            pe_diff = ((company_pe - result['industry_pe']) / result['industry_pe']) * 100
            result['pe_vs_industry'] = f"{'Premium' if pe_diff > 0 else 'Discount'} of {abs(pe_diff):.1f}%"
            result['pe_premium_discount'] = pe_diff
        
        if company_ev_ebitda and result['industry_ev_ebitda']:
            ev_diff = ((company_ev_ebitda - result['industry_ev_ebitda']) / result['industry_ev_ebitda']) * 100
            result['ev_ebitda_vs_industry'] = f"{'Premium' if ev_diff > 0 else 'Discount'} of {abs(ev_diff):.1f}%"
        
        return result
    
    def get_wacc_benchmark(
        self,
        sector: str,
        industry: Optional[str] = None
    ) -> Dict:
        """
        Get industry WACC benchmark for DCF.
        
        Returns:
            Dict with industry WACC components
        """
        industry_name = self.get_industry_name(sector, industry)
        benchmarks = self.damodaran.get_all_benchmarks(industry_name)
        
        wacc_data = benchmarks.get('wacc', {})
        beta_data = benchmarks.get('betas', {})
        
        return {
            'industry': industry_name,
            'industry_wacc': wacc_data.get('wacc'),
            'industry_cost_of_equity': wacc_data.get('cost_of_equity'),
            'industry_cost_of_debt': wacc_data.get('cost_of_debt'),
            'industry_unlevered_beta': beta_data.get('unlevered_beta'),
            'industry_levered_beta': beta_data.get('levered_beta'),
            'industry_d_e_ratio': beta_data.get('d_e_ratio'),
        }
    
    def _find_metric_in_benchmarks(self, metric: str, benchmarks: Dict) -> Optional[float]:
        """Find a metric value in the benchmarks dict."""
        # Map metric names to benchmark categories
        metric_map = {
            'pe_ratio': ('multiples', 'pe_ratio'),
            'ev_ebitda': ('multiples', 'ev_ebitda'),
            'peg_ratio': ('multiples', 'peg_ratio'),
            'roe': ('profitability', 'roe'),
            'roa': ('profitability', 'roa'),
            'roic': ('profitability', 'roic'),
            'gross_margin': ('margins', 'gross_margin'),
            'operating_margin': ('margins', 'operating_margin'),
            'net_margin': ('margins', 'net_margin'),
            'wacc': ('wacc', 'wacc'),
            'cost_of_equity': ('wacc', 'cost_of_equity'),
            'cost_of_debt': ('wacc', 'cost_of_debt'),
            'beta': ('betas', 'levered_beta'),
            'levered_beta': ('betas', 'levered_beta'),
            'unlevered_beta': ('betas', 'unlevered_beta'),
            'd_e_ratio': ('betas', 'd_e_ratio'),
            'debt_equity': ('betas', 'd_e_ratio'),
        }
        
        if metric not in metric_map:
            return None
        
        category, key = metric_map[metric]
        return benchmarks.get(category, {}).get(key)
    
    def _generate_interpretation(
        self,
        metric: str,
        company_value: float,
        industry_value: float,
        diff_percent: float,
        is_better: Optional[bool],
        industry_name: str
    ) -> str:
        """Generate human-readable interpretation."""
        metric_name = self.METRIC_NAMES.get(metric, metric)
        direction = self.METRIC_DIRECTIONS.get(metric, 'neutral')
        
        abs_diff = abs(diff_percent)
        
        if abs_diff < 5:
            position = "in line with"
            quality = "neutral"
        elif diff_percent > 0:
            position = f"{abs_diff:.0f}% above"
            quality = "favorable" if direction == 'higher' else ("unfavorable" if direction == 'lower' else "")
        else:
            position = f"{abs_diff:.0f}% below"
            quality = "favorable" if direction == 'lower' else ("unfavorable" if direction == 'higher' else "")
        
        interpretation = f"{metric_name} is {position} the {industry_name} industry average"
        
        if quality:
            interpretation += f" ({quality})"
        
        return interpretation


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_sector_benchmarks(
    sector: str,
    industry: Optional[str] = None,
    company_metrics: Optional[Dict[str, float]] = None
) -> Dict:
    """
    Get sector benchmarks for a company.
    
    Args:
        sector: GICS sector
        industry: Optional GICS industry
        company_metrics: Optional company metrics to compare
        
    Returns:
        Dict with benchmarks and comparisons
    """
    sb = SectorBenchmarks()
    return sb.get_benchmarks_for_company(sector, industry, company_metrics)


def compare_to_industry(
    metric: str,
    company_value: float,
    sector: str,
    industry: Optional[str] = None
) -> BenchmarkComparison:
    """
    Compare a single metric to industry benchmark.
    
    Args:
        metric: Metric name
        company_value: Company's value
        sector: GICS sector
        industry: Optional GICS industry
        
    Returns:
        BenchmarkComparison result
    """
    sb = SectorBenchmarks()
    return sb.compare_metric(metric, company_value, sector, industry)


# ==========================================
# INTEGRATION WITH ATLAS
# ==========================================

def enrich_financials_with_benchmarks(
    financials: Dict,
    sector: str,
    industry: Optional[str] = None
) -> Dict:
    """
    Add industry benchmark context to extracted financials.
    
    Args:
        financials: ATLAS extracted financials dict
        sector: Company's GICS sector
        industry: Optional GICS industry
        
    Returns:
        Financials dict with added 'benchmarks' section
    """
    sb = SectorBenchmarks()
    
    # Extract metrics to compare
    company_metrics = {}
    
    # P/E ratio
    if 'market_data' in financials:
        pe = financials['market_data'].get('pe_ratio')
        if pe:
            company_metrics['pe_ratio'] = pe
    
    # Profitability metrics from ratios
    if 'key_ratios' in financials:
        ratios = financials['key_ratios']
        if ratios.get('roe'):
            company_metrics['roe'] = ratios['roe']
        if ratios.get('roa'):
            company_metrics['roa'] = ratios['roa']
        if ratios.get('operating_margin'):
            company_metrics['operating_margin'] = ratios['operating_margin']
        if ratios.get('gross_margin'):
            company_metrics['gross_margin'] = ratios['gross_margin']
        if ratios.get('debt_to_equity'):
            company_metrics['debt_equity'] = ratios['debt_to_equity']
    
    # Get benchmarks
    benchmarks_result = sb.get_benchmarks_for_company(
        sector=sector,
        industry=industry,
        company_metrics=company_metrics
    )
    
    # Add to financials
    financials['industry_benchmarks'] = benchmarks_result
    
    return financials


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("SECTOR BENCHMARKS TEST")
    print("=" * 60)
    
    # Test with Apple-like metrics
    company_metrics = {
        'pe_ratio': 28.5,
        'roe': 1.45,  # 145% ROE
        'operating_margin': 0.30,  # 30%
        'gross_margin': 0.45,  # 45%
    }
    
    result = get_sector_benchmarks(
        sector="Technology",
        industry="Software",
        company_metrics=company_metrics
    )
    
    print(f"\nIndustry: {result['industry']}")
    print("\nComparisons:")
    for metric, comp in result['comparisons'].items():
        status = "+" if comp['is_better'] else ("-" if comp['is_better'] is False else "~")
        print(f"  [{status}] {metric}: {comp['company']:.2f} vs {comp['industry']:.2f} ({comp['diff_percent']:.1f}%)")
        print(f"      {comp['interpretation']}")
    
    print("\n[OK] Module ready for integration")

