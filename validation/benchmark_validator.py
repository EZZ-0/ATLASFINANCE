"""
Benchmark Validator for ATLAS Financial Intelligence
=====================================================

Compares ATLAS-extracted metrics against external sources (Yahoo Finance, Bloomberg)
to measure accuracy and identify discrepancies.

Author: ATLAS Financial Intelligence
Date: 2025-12-07
"""

import yfinance as yf
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationStatus(Enum):
    """Validation result status."""
    PASS = "PASS"           # Within tolerance
    WARNING = "WARNING"     # Close to tolerance limit
    FAIL = "FAIL"           # Exceeds tolerance
    MISSING = "MISSING"     # Data not available
    SKIP = "SKIP"           # Comparison not applicable


@dataclass
class MetricComparison:
    """Result of comparing a single metric."""
    metric_name: str
    atlas_value: Optional[float]
    external_value: Optional[float]
    external_source: str
    difference_percent: Optional[float]
    status: ValidationStatus
    notes: str = ""


@dataclass
class ValidationReport:
    """Complete validation report for a ticker."""
    ticker: str
    comparisons: List[MetricComparison]
    overall_accuracy: float
    pass_rate: float
    timestamp: str
    
    def to_markdown(self) -> str:
        """Generate markdown report."""
        lines = [
            f"# Validation Report: {self.ticker}",
            f"**Generated:** {self.timestamp}",
            f"**Overall Accuracy:** {self.overall_accuracy:.1f}%",
            f"**Pass Rate:** {self.pass_rate:.1f}%",
            "",
            "| Metric | ATLAS | External | Diff % | Status |",
            "|--------|-------|----------|--------|--------|"
        ]
        
        for comp in self.comparisons:
            atlas = f"{comp.atlas_value:.2f}" if comp.atlas_value is not None else "N/A"
            ext = f"{comp.external_value:.2f}" if comp.external_value is not None else "N/A"
            diff = f"{comp.difference_percent:.1f}%" if comp.difference_percent is not None else "N/A"
            status_icon = {
                ValidationStatus.PASS: "✅",
                ValidationStatus.WARNING: "⚠️",
                ValidationStatus.FAIL: "❌",
                ValidationStatus.MISSING: "❓",
                ValidationStatus.SKIP: "⏭️"
            }.get(comp.status, "?")
            
            lines.append(f"| {comp.metric_name} | {atlas} | {ext} | {diff} | {status_icon} |")
        
        return "\n".join(lines)


class BenchmarkValidator:
    """
    Validates ATLAS metrics against external sources.
    
    Usage:
        validator = BenchmarkValidator()
        report = validator.validate_ticker("AAPL", atlas_financials)
        print(report.to_markdown())
    """
    
    # Default tolerance thresholds (percentage difference allowed)
    DEFAULT_TOLERANCES = {
        'pe_ratio': 5.0,           # P/E can vary by reporting period
        'price_to_book': 5.0,
        'roe': 10.0,               # ROE definitions vary
        'roa': 10.0,
        'debt_to_equity': 10.0,
        'current_ratio': 5.0,
        'quick_ratio': 5.0,
        'gross_margin': 5.0,
        'operating_margin': 5.0,
        'net_margin': 5.0,
        'revenue': 2.0,            # Revenue should match closely
        'net_income': 5.0,
        'eps': 3.0,
        'market_cap': 2.0,
        'beta': 10.0,
        'dividend_yield': 5.0,
    }
    
    # Warning threshold is 80% of fail threshold
    WARNING_MULTIPLIER = 0.8
    
    def __init__(self, tolerances: Optional[Dict[str, float]] = None):
        """
        Initialize validator with custom tolerances if provided.
        
        Args:
            tolerances: Dict of metric_name -> allowed_percent_difference
        """
        self.tolerances = {**self.DEFAULT_TOLERANCES}
        if tolerances:
            self.tolerances.update(tolerances)
    
    def _fetch_yahoo_data(self, ticker: str) -> Dict:
        """Fetch comparison data from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'gross_margin': info.get('grossMargins'),
                'operating_margin': info.get('operatingMargins'),
                'net_margin': info.get('profitMargins'),
                'revenue': info.get('totalRevenue'),
                'net_income': info.get('netIncomeToCommon'),
                'eps': info.get('trailingEps'),
                'market_cap': info.get('marketCap'),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield'),
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            }
        except Exception as e:
            logger.error(f"Failed to fetch Yahoo data for {ticker}: {e}")
            return {}
    
    def _compare_metric(
        self, 
        metric_name: str, 
        atlas_value: Optional[float], 
        external_value: Optional[float],
        external_source: str = "Yahoo Finance"
    ) -> MetricComparison:
        """Compare a single metric and return result."""
        
        # Handle missing data
        if atlas_value is None and external_value is None:
            return MetricComparison(
                metric_name=metric_name,
                atlas_value=None,
                external_value=None,
                external_source=external_source,
                difference_percent=None,
                status=ValidationStatus.SKIP,
                notes="Both sources missing data"
            )
        
        if atlas_value is None:
            return MetricComparison(
                metric_name=metric_name,
                atlas_value=None,
                external_value=external_value,
                external_source=external_source,
                difference_percent=None,
                status=ValidationStatus.MISSING,
                notes="ATLAS value missing"
            )
        
        if external_value is None:
            return MetricComparison(
                metric_name=metric_name,
                atlas_value=atlas_value,
                external_value=None,
                external_source=external_source,
                difference_percent=None,
                status=ValidationStatus.MISSING,
                notes="External value missing"
            )
        
        # Handle zero division
        if external_value == 0:
            if atlas_value == 0:
                return MetricComparison(
                    metric_name=metric_name,
                    atlas_value=0,
                    external_value=0,
                    external_source=external_source,
                    difference_percent=0.0,
                    status=ValidationStatus.PASS,
                    notes="Both zero"
                )
            else:
                return MetricComparison(
                    metric_name=metric_name,
                    atlas_value=atlas_value,
                    external_value=0,
                    external_source=external_source,
                    difference_percent=None,
                    status=ValidationStatus.FAIL,
                    notes="External is zero, cannot calculate %"
                )
        
        # Calculate percentage difference
        diff_percent = abs((atlas_value - external_value) / external_value) * 100
        
        # Determine status based on tolerance
        tolerance = self.tolerances.get(metric_name, 10.0)
        warning_threshold = tolerance * self.WARNING_MULTIPLIER
        
        if diff_percent <= warning_threshold:
            status = ValidationStatus.PASS
        elif diff_percent <= tolerance:
            status = ValidationStatus.WARNING
        else:
            status = ValidationStatus.FAIL
        
        return MetricComparison(
            metric_name=metric_name,
            atlas_value=atlas_value,
            external_value=external_value,
            external_source=external_source,
            difference_percent=diff_percent,
            status=status
        )
    
    def validate_ticker(
        self, 
        ticker: str, 
        atlas_financials: Dict
    ) -> ValidationReport:
        """
        Validate ATLAS extraction against external sources.
        
        Args:
            ticker: Stock ticker symbol
            atlas_financials: Dict of financials extracted by ATLAS
        
        Returns:
            ValidationReport with all comparison results
        """
        from datetime import datetime
        
        # Fetch external data
        yahoo_data = self._fetch_yahoo_data(ticker)
        
        # Map ATLAS field names to our standard names
        atlas_mapped = self._map_atlas_fields(atlas_financials)
        
        # Compare each metric
        comparisons = []
        metrics_to_compare = [
            'pe_ratio', 'price_to_book', 'roe', 'roa', 
            'debt_to_equity', 'current_ratio', 'gross_margin',
            'operating_margin', 'net_margin', 'eps', 'beta',
            'dividend_yield', 'market_cap'
        ]
        
        for metric in metrics_to_compare:
            comparison = self._compare_metric(
                metric_name=metric,
                atlas_value=atlas_mapped.get(metric),
                external_value=yahoo_data.get(metric)
            )
            comparisons.append(comparison)
        
        # Calculate overall metrics
        valid_comparisons = [c for c in comparisons if c.status not in [ValidationStatus.SKIP, ValidationStatus.MISSING]]
        pass_count = sum(1 for c in valid_comparisons if c.status == ValidationStatus.PASS)
        total_valid = len(valid_comparisons)
        
        # Calculate weighted accuracy (100% - average absolute error)
        errors = [c.difference_percent for c in valid_comparisons if c.difference_percent is not None]
        avg_error = sum(errors) / len(errors) if errors else 0
        overall_accuracy = max(0, 100 - avg_error)
        
        pass_rate = (pass_count / total_valid * 100) if total_valid > 0 else 0
        
        return ValidationReport(
            ticker=ticker,
            comparisons=comparisons,
            overall_accuracy=overall_accuracy,
            pass_rate=pass_rate,
            timestamp=datetime.now().isoformat()
        )
    
    def _map_atlas_fields(self, financials: Dict) -> Dict:
        """Map ATLAS field names to standard comparison names."""
        # Handle nested structures and various naming conventions
        mapped = {}
        
        # Direct mappings
        field_map = {
            'pe_ratio': ['pe_ratio', 'trailingPE', 'PE', 'p_e_ratio'],
            'price_to_book': ['price_to_book', 'priceToBook', 'PB', 'p_b_ratio'],
            'roe': ['roe', 'returnOnEquity', 'ROE', 'return_on_equity'],
            'roa': ['roa', 'returnOnAssets', 'ROA', 'return_on_assets'],
            'debt_to_equity': ['debt_to_equity', 'debtToEquity', 'D/E', 'debt_equity'],
            'current_ratio': ['current_ratio', 'currentRatio'],
            'gross_margin': ['gross_margin', 'grossMargins', 'gross_profit_margin'],
            'operating_margin': ['operating_margin', 'operatingMargins', 'op_margin'],
            'net_margin': ['net_margin', 'profitMargins', 'net_profit_margin'],
            'eps': ['eps', 'trailingEps', 'EPS', 'earnings_per_share'],
            'beta': ['beta', 'Beta'],
            'dividend_yield': ['dividend_yield', 'dividendYield', 'div_yield'],
            'market_cap': ['market_cap', 'marketCap', 'market_capitalization'],
        }
        
        for standard_name, possible_names in field_map.items():
            for name in possible_names:
                if name in financials:
                    value = financials[name]
                    # Handle percentage values stored as decimals
                    if standard_name in ['roe', 'roa', 'gross_margin', 'operating_margin', 'net_margin', 'dividend_yield']:
                        if value is not None and abs(value) < 1:
                            value = value  # Already in decimal form
                    mapped[standard_name] = value
                    break
        
        return mapped


def validate_metrics(ticker: str, atlas_financials: Dict) -> ValidationReport:
    """
    Convenience function to validate metrics for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        atlas_financials: Dict of financials from ATLAS extraction
    
    Returns:
        ValidationReport with results
    """
    validator = BenchmarkValidator()
    return validator.validate_ticker(ticker, atlas_financials)


# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    sample_atlas_data = {
        'pe_ratio': 28.5,
        'roe': 0.145,
        'debt_to_equity': 1.87,
        'current_ratio': 0.94,
        'eps': 6.43,
        'beta': 1.25,
    }
    
    print("Testing BenchmarkValidator with AAPL...")
    report = validate_metrics("AAPL", sample_atlas_data)
    print(report.to_markdown())

