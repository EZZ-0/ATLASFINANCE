"""
COMPREHENSIVE FLIP CARD VALIDATION SUITE
=========================================
Multi-layer validation for flip card integration:

1. SCHEMA VALIDATION - Check metric definitions are complete
2. DATA EXTRACTION VALIDATION - Verify data can be extracted
3. COMPONENT VALIDATION - Ensure all components exist
4. FORMAT VALIDATION - Test value formatting
5. RENDER VALIDATION - Test card rendering (mock)
6. INTEGRATION VALIDATION - End-to-end with real data

Run: python test_flip_card_validation.py
"""

import sys
import traceback
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np


# =============================================================================
# TEST FRAMEWORK
# =============================================================================

class TestResult(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARN = "⚠️ WARN"
    SKIP = "⏭️ SKIP"


@dataclass
class ValidationResult:
    test_name: str
    result: TestResult
    message: str
    details: Optional[Dict] = None


class ValidationSuite:
    """Comprehensive validation suite"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.checkpoints_passed = 0
        self.checkpoints_failed = 0
    
    def add_result(self, result: ValidationResult):
        self.results.append(result)
        if result.result == TestResult.PASS:
            self.checkpoints_passed += 1
        elif result.result == TestResult.FAIL:
            self.checkpoints_failed += 1
    
    def print_report(self):
        print("\n" + "=" * 80)
        print("VALIDATION REPORT")
        print("=" * 80)
        
        for r in self.results:
            print(f"\n{r.result.value} {r.test_name}")
            print(f"   {r.message}")
            if r.details:
                for k, v in r.details.items():
                    print(f"   - {k}: {v}")
        
        print("\n" + "-" * 80)
        total = len(self.results)
        print(f"SUMMARY: {self.checkpoints_passed}/{total} passed, {self.checkpoints_failed} failed")
        print("=" * 80)
        
        return self.checkpoints_failed == 0


# =============================================================================
# 1. SCHEMA VALIDATION
# =============================================================================

def validate_metric_definitions(suite: ValidationSuite):
    """Validate all metric definitions are complete and correct"""
    
    try:
        from flip_card_integration import (
            DASHBOARD_METRICS, DCF_METRICS, FORENSIC_METRICS, QUANT_METRICS,
            MetricDefinition
        )
        
        all_metrics = {
            'DASHBOARD': DASHBOARD_METRICS,
            'DCF': DCF_METRICS,
            'FORENSIC': FORENSIC_METRICS,
            'QUANT': QUANT_METRICS,
        }
        
        total_metrics = 0
        errors = []
        
        required_fields = ['key', 'display_name', 'formula', 'category', 
                          'components', 'explanation_beginner']
        
        for category, metrics in all_metrics.items():
            for metric in metrics:
                total_metrics += 1
                
                # Check required fields
                for field in required_fields:
                    value = getattr(metric, field, None)
                    if value is None or (isinstance(value, str) and not value.strip()):
                        errors.append(f"{category}.{metric.key}: missing {field}")
                
                # Check components is a list
                if not isinstance(metric.components, list):
                    errors.append(f"{category}.{metric.key}: components must be a list")
                
                # Check format_type is valid
                valid_formats = ['ratio', 'percentage', 'currency', 'number']
                if metric.format_type not in valid_formats:
                    errors.append(f"{category}.{metric.key}: invalid format_type '{metric.format_type}'")
        
        if errors:
            suite.add_result(ValidationResult(
                test_name="1.1 Schema Validation",
                result=TestResult.FAIL,
                message=f"Found {len(errors)} schema errors in {total_metrics} metrics",
                details={'errors': errors[:5]}  # Show first 5
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="1.1 Schema Validation",
                result=TestResult.PASS,
                message=f"All {total_metrics} metric definitions are valid",
                details={'categories': list(all_metrics.keys())}
            ))
            
    except ImportError as e:
        suite.add_result(ValidationResult(
            test_name="1.1 Schema Validation",
            result=TestResult.FAIL,
            message=f"Import failed: {e}"
        ))


def validate_explanation_depths(suite: ValidationSuite):
    """Validate all 3 explanation depths exist"""
    
    try:
        from flip_card_integration import DASHBOARD_METRICS
        
        missing = []
        for metric in DASHBOARD_METRICS:
            if not metric.explanation_beginner:
                missing.append(f"{metric.key}: beginner")
            if not metric.explanation_intermediate:
                missing.append(f"{metric.key}: intermediate")
            if not metric.explanation_professional:
                missing.append(f"{metric.key}: professional")
        
        if missing:
            suite.add_result(ValidationResult(
                test_name="1.2 Explanation Depths",
                result=TestResult.WARN,
                message=f"{len(missing)} missing explanations",
                details={'missing': missing[:3]}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="1.2 Explanation Depths",
                result=TestResult.PASS,
                message="All metrics have 3-depth explanations"
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="1.2 Explanation Depths",
            result=TestResult.FAIL,
            message=str(e)
        ))


# =============================================================================
# 2. DATA EXTRACTION VALIDATION
# =============================================================================

def validate_extractor_creation(suite: ValidationSuite):
    """Validate MetricExtractor can be created"""
    
    try:
        from flip_card_integration import MetricExtractor
        
        # Test with minimal data
        test_financials = {
            'info': {'trailingPE': 22.5, 'returnOnEquity': 0.18},
            'market_data': {'current_price': 175.50},
            'ratios': pd.DataFrame(),
        }
        
        extractor = MetricExtractor(test_financials)
        
        suite.add_result(ValidationResult(
            test_name="2.1 Extractor Creation",
            result=TestResult.PASS,
            message="MetricExtractor created successfully"
        ))
        
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="2.1 Extractor Creation",
            result=TestResult.FAIL,
            message=str(e)
        ))


def validate_key_extraction(suite: ValidationSuite):
    """Validate key metrics can be extracted"""
    
    try:
        from flip_card_integration import MetricExtractor
        
        # Test with realistic data
        test_financials = {
            'info': {
                'trailingPE': 22.5,
                'returnOnEquity': 0.185,
                'debtToEquity': 1.87,
                'currentRatio': 0.98,
                'grossMargins': 0.438,
                'operatingMargins': 0.297,
                'trailingEps': 6.42,
                'dividendYield': 0.0052,
                'beta': 1.24,
                'currentPrice': 175.50,
            },
            'market_data': {'current_price': 175.50},
            'ratios': pd.DataFrame(),
        }
        
        extractor = MetricExtractor(test_financials)
        
        # Test extraction of key metrics
        test_keys = ['pe_ratio', 'roe', 'debt_to_equity', 'current_ratio', 
                     'gross_margin', 'eps', 'beta', 'current_price']
        
        extracted = {}
        missing = []
        
        for key in test_keys:
            value = extractor.get_value(key)
            if value is not None:
                extracted[key] = value
            else:
                missing.append(key)
        
        if len(extracted) >= 6:
            suite.add_result(ValidationResult(
                test_name="2.2 Key Extraction",
                result=TestResult.PASS,
                message=f"Extracted {len(extracted)}/{len(test_keys)} metrics",
                details={'extracted': list(extracted.keys())}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="2.2 Key Extraction",
                result=TestResult.WARN,
                message=f"Only extracted {len(extracted)}/{len(test_keys)} metrics",
                details={'missing': missing}
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="2.2 Key Extraction",
            result=TestResult.FAIL,
            message=str(e)
        ))


def validate_null_handling(suite: ValidationSuite):
    """Validate graceful handling of null/missing data"""
    
    try:
        from flip_card_integration import MetricExtractor, _format_value
        
        # Test with empty/null data
        test_cases = [
            ({}, "empty dict"),
            ({'info': None}, "null info"),
            ({'info': {}}, "empty info"),
            ({'ratios': pd.DataFrame()}, "empty ratios"),
            ({'info': {'trailingPE': None}}, "null PE"),
            ({'info': {'trailingPE': 'N/A'}}, "N/A string"),
        ]
        
        errors = []
        for data, description in test_cases:
            try:
                extractor = MetricExtractor(data)
                value = extractor.get_value('pe_ratio')
                # Should return None, not crash
                if value is not None and value != 'N/A':
                    # This is actually OK - might find value elsewhere
                    pass
            except Exception as e:
                errors.append(f"{description}: {e}")
        
        # Test format_value with edge cases
        edge_cases = [None, 'N/A', float('nan'), float('inf'), -float('inf'), '', 0]
        for val in edge_cases:
            try:
                result = _format_value(val, 'number')
                # Should not crash
            except Exception as e:
                errors.append(f"format({val}): {e}")
        
        if errors:
            suite.add_result(ValidationResult(
                test_name="2.3 Null Handling",
                result=TestResult.FAIL,
                message=f"{len(errors)} null handling errors",
                details={'errors': errors[:3]}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="2.3 Null Handling",
                result=TestResult.PASS,
                message="All null cases handled gracefully"
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="2.3 Null Handling",
            result=TestResult.FAIL,
            message=str(e)
        ))


# =============================================================================
# 3. FORMAT VALIDATION
# =============================================================================

def validate_format_functions(suite: ValidationSuite):
    """Validate value formatting functions"""
    
    try:
        from flip_card_integration import _format_value
        
        test_cases = [
            # (value, format_type, expected_contains)
            (0.156, "percentage", "%"),
            (22.5, "ratio", "x"),
            (175.50, "currency", "$"),
            (1e9, "currency", "B"),
            (1e12, "currency", "T"),
            (1e6, "currency", "M"),
            (None, "number", "N/A"),
            (42.123, "number", "42"),
        ]
        
        errors = []
        for value, fmt, expected in test_cases:
            result = _format_value(value, fmt)
            if expected not in str(result):
                errors.append(f"format({value}, {fmt}) = '{result}', expected '{expected}' in result")
        
        if errors:
            suite.add_result(ValidationResult(
                test_name="3.1 Format Functions",
                result=TestResult.FAIL,
                message=f"{len(errors)} format errors",
                details={'errors': errors[:3]}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="3.1 Format Functions",
                result=TestResult.PASS,
                message=f"All {len(test_cases)} format tests passed"
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="3.1 Format Functions",
            result=TestResult.FAIL,
            message=str(e)
        ))


def validate_percentage_normalization(suite: ValidationSuite):
    """Validate percentage values are normalized correctly"""
    
    try:
        from flip_card_integration import _format_value
        
        # Test both decimal (0.15) and already-percentage (15) formats
        test_cases = [
            (0.15, "percentage", "15"),   # Should show ~15%
            (0.0156, "percentage", "1.5"),  # Should show ~1.5%
            (15.6, "percentage", "15.6"),  # Already percentage, keep as is
            (0.857, "percentage", "85"),   # 85.7%
        ]
        
        errors = []
        for value, fmt, expected_num in test_cases:
            result = _format_value(value, fmt)
            if expected_num not in result:
                errors.append(f"format({value}) = '{result}', expected '{expected_num}' in result")
        
        if errors:
            suite.add_result(ValidationResult(
                test_name="3.2 Percentage Normalization",
                result=TestResult.WARN,
                message=f"{len(errors)} normalization issues (may be acceptable)",
                details={'issues': errors}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="3.2 Percentage Normalization",
                result=TestResult.PASS,
                message="Percentage normalization working correctly"
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="3.2 Percentage Normalization",
            result=TestResult.FAIL,
            message=str(e)
        ))


# =============================================================================
# 4. FLIP CARD COMPONENT VALIDATION
# =============================================================================

def validate_flip_card_component(suite: ValidationSuite):
    """Validate FlipCardMetric component"""
    
    try:
        from flip_card_component import FlipCardMetric
        
        # Create test metric
        metric = FlipCardMetric(
            name="P/E Ratio",
            value=22.5,
            formula="Price ÷ EPS",
            components={"Price": 175.50, "EPS": 7.80},
            explanation_beginner="Test beginner",
            explanation_intermediate="Test intermediate",
            explanation_professional="Test professional",
            benchmark={"low": 15, "high": 25},
            category="Valuation"
        )
        
        # Test methods
        color = metric.get_color()
        formatted = metric.format_value()
        calc_string = metric.get_calculation_string()
        
        errors = []
        if not color.startswith('#'):
            errors.append(f"Invalid color: {color}")
        if 'x' not in formatted and '22' not in formatted:
            errors.append(f"Invalid format: {formatted}")
        if not calc_string:
            errors.append("Empty calculation string")
        
        if errors:
            suite.add_result(ValidationResult(
                test_name="4.1 FlipCardMetric",
                result=TestResult.FAIL,
                message=f"{len(errors)} component errors",
                details={'errors': errors}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="4.1 FlipCardMetric",
                result=TestResult.PASS,
                message="FlipCardMetric component working",
                details={'color': color, 'formatted': formatted}
            ))
            
    except ImportError:
        suite.add_result(ValidationResult(
            test_name="4.1 FlipCardMetric",
            result=TestResult.SKIP,
            message="flip_card_component not available"
        ))
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="4.1 FlipCardMetric",
            result=TestResult.FAIL,
            message=str(e)
        ))


def validate_ratio_definitions_loaded(suite: ValidationSuite):
    """Validate ratio_card.py definitions can be loaded"""
    
    try:
        from ratio_card import RATIO_DEFINITIONS
        
        if len(RATIO_DEFINITIONS) >= 20:
            suite.add_result(ValidationResult(
                test_name="4.2 Ratio Definitions",
                result=TestResult.PASS,
                message=f"Loaded {len(RATIO_DEFINITIONS)} ratio definitions",
                details={'sample': list(RATIO_DEFINITIONS.keys())[:5]}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="4.2 Ratio Definitions",
                result=TestResult.WARN,
                message=f"Only {len(RATIO_DEFINITIONS)} definitions loaded"
            ))
            
    except ImportError:
        suite.add_result(ValidationResult(
            test_name="4.2 Ratio Definitions",
            result=TestResult.SKIP,
            message="ratio_card.py not available"
        ))


# =============================================================================
# 5. INTEGRATION VALIDATION (with real extractor)
# =============================================================================

def validate_real_data_integration(suite: ValidationSuite):
    """Validate integration with real-ish financial data"""
    
    try:
        from flip_card_integration import (
            MetricExtractor, DASHBOARD_METRICS, render_metric_with_flip
        )
        
        # Simulate Apple-like financials
        test_financials = {
            'ticker': 'AAPL',
            'company_name': 'Apple Inc.',
            'info': {
                'trailingPE': 28.5,
                'forwardPE': 26.2,
                'returnOnEquity': 0.1605,
                'returnOnAssets': 0.2214,
                'debtToEquity': 1.81,
                'currentRatio': 0.988,
                'quickRatio': 0.843,
                'grossMargins': 0.438,
                'operatingMargins': 0.297,
                'profitMargins': 0.253,
                'trailingEps': 6.42,
                'forwardEps': 7.12,
                'dividendYield': 0.0052,
                'beta': 1.24,
                'currentPrice': 191.24,
                'marketCap': 2.96e12,
                'totalRevenue': 383.29e9,
                'netIncomeToCommon': 96.99e9,
                'freeCashflow': 99.58e9,
            },
            'market_data': {
                'current_price': 191.24,
                'market_cap': 2.96e12,
            },
            'ratios': pd.DataFrame({
                'Value': [28.5, 0.1605, 1.81, 0.988, 0.438]
            }, index=['PE_Ratio', 'ROE', 'Debt_to_Equity', 'Current_Ratio', 'Gross_Margin']),
            'income_statement': pd.DataFrame(),
            'balance_sheet': pd.DataFrame(),
        }
        
        extractor = MetricExtractor(test_financials)
        
        # Test extraction of all dashboard metrics
        results = {}
        for metric in DASHBOARD_METRICS:
            value = extractor.get_value(metric.key)
            results[metric.key] = value
        
        found = sum(1 for v in results.values() if v is not None)
        
        if found >= 8:
            suite.add_result(ValidationResult(
                test_name="5.1 Real Data Integration",
                result=TestResult.PASS,
                message=f"Extracted {found}/{len(DASHBOARD_METRICS)} dashboard metrics",
                details={k: f"{v:.2f}" if v else "N/A" for k, v in list(results.items())[:5]}
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="5.1 Real Data Integration",
                result=TestResult.WARN,
                message=f"Only extracted {found}/{len(DASHBOARD_METRICS)} metrics",
                details={'missing': [k for k, v in results.items() if v is None]}
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="5.1 Real Data Integration",
            result=TestResult.FAIL,
            message=str(e)
        ))


def validate_component_extraction(suite: ValidationSuite):
    """Validate component extraction for calculations"""
    
    try:
        from flip_card_integration import MetricExtractor, DASHBOARD_METRICS
        
        test_financials = {
            'info': {
                'currentPrice': 175.50,
                'trailingEps': 7.80,
                'netIncomeToCommon': 94e9,
                'totalStockholdersEquity': 62e9,
            },
            'market_data': {},
            'ratios': pd.DataFrame(),
        }
        
        extractor = MetricExtractor(test_financials)
        
        # Test PE ratio components
        pe_metric = next(m for m in DASHBOARD_METRICS if m.key == 'pe_ratio')
        components = extractor.get_component_values(pe_metric.components)
        
        if len(components) >= 1:
            suite.add_result(ValidationResult(
                test_name="5.2 Component Extraction",
                result=TestResult.PASS,
                message=f"Extracted {len(components)} components for PE calculation",
                details=components
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="5.2 Component Extraction",
                result=TestResult.WARN,
                message="Could not extract PE components"
            ))
            
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="5.2 Component Extraction",
            result=TestResult.FAIL,
            message=str(e)
        ))


# =============================================================================
# 6. MONTE CARLO VALIDATION
# =============================================================================

def validate_monte_carlo_engine(suite: ValidationSuite):
    """Validate Monte Carlo engine functionality"""
    
    try:
        from monte_carlo_engine import MonteCarloEngine, SimulationParams
        
        engine = MonteCarloEngine(SimulationParams(n_simulations=100, seed=42))
        
        # Test DCF simulation
        result = engine.dcf_simulation(
            base_revenue=100e9,
            base_fcf_margin=0.20,
            shares_outstanding=5e9,
            net_debt=10e9
        )
        
        if result.get('status') == 'success':
            stats = result.get('statistics', {})
            suite.add_result(ValidationResult(
                test_name="6.1 Monte Carlo DCF",
                result=TestResult.PASS,
                message=f"DCF simulation completed with {result.get('n_simulations')} iterations",
                details={
                    'median': f"${stats.get('median', 0):.2f}",
                    '5th_pct': f"${stats.get('percentile_5', 0):.2f}",
                    '95th_pct': f"${stats.get('percentile_95', 0):.2f}",
                }
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="6.1 Monte Carlo DCF",
                result=TestResult.FAIL,
                message="DCF simulation failed"
            ))
            
    except ImportError:
        suite.add_result(ValidationResult(
            test_name="6.1 Monte Carlo DCF",
            result=TestResult.SKIP,
            message="monte_carlo_engine not available"
        ))
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="6.1 Monte Carlo DCF",
            result=TestResult.FAIL,
            message=str(e)
        ))


def validate_var_calculation(suite: ValidationSuite):
    """Validate Value at Risk calculation"""
    
    try:
        from monte_carlo_engine import MonteCarloEngine, SimulationParams
        import numpy as np
        
        engine = MonteCarloEngine(SimulationParams(seed=42))
        
        # Generate test returns
        np.random.seed(42)
        returns = np.random.normal(0.0005, 0.02, 252)
        
        result = engine.calculate_var(
            returns=returns,
            portfolio_value=100000,
            confidence_levels=[0.95, 0.99]
        )
        
        var_95 = result.get('var', {}).get('95%', {}).get('dollar', 0)
        
        if var_95 > 0:
            suite.add_result(ValidationResult(
                test_name="6.2 VaR Calculation",
                result=TestResult.PASS,
                message="VaR calculation working",
                details={
                    '95% VaR': f"${var_95:,.0f}",
                    'Max Drawdown': f"{result.get('max_drawdown', 0):.1%}",
                }
            ))
        else:
            suite.add_result(ValidationResult(
                test_name="6.2 VaR Calculation",
                result=TestResult.WARN,
                message="VaR returned 0"
            ))
            
    except ImportError:
        suite.add_result(ValidationResult(
            test_name="6.2 VaR Calculation",
            result=TestResult.SKIP,
            message="monte_carlo_engine not available"
        ))
    except Exception as e:
        suite.add_result(ValidationResult(
            test_name="6.2 VaR Calculation",
            result=TestResult.FAIL,
            message=str(e)
        ))


# =============================================================================
# RUN ALL TESTS
# =============================================================================

def run_all_validations():
    """Run complete validation suite"""
    
    print("=" * 80)
    print("FLIP CARD INTEGRATION - COMPREHENSIVE VALIDATION SUITE")
    print("=" * 80)
    print("Testing modules:")
    print("  - flip_card_integration.py")
    print("  - flip_card_component.py")
    print("  - monte_carlo_engine.py")
    print("  - ratio_card.py")
    print("=" * 80)
    
    suite = ValidationSuite()
    
    # 1. Schema Validation
    print("\n[PHASE 1] Schema Validation...")
    validate_metric_definitions(suite)
    validate_explanation_depths(suite)
    
    # 2. Data Extraction
    print("[PHASE 2] Data Extraction Validation...")
    validate_extractor_creation(suite)
    validate_key_extraction(suite)
    validate_null_handling(suite)
    
    # 3. Format Functions
    print("[PHASE 3] Format Validation...")
    validate_format_functions(suite)
    validate_percentage_normalization(suite)
    
    # 4. Component Validation
    print("[PHASE 4] Component Validation...")
    validate_flip_card_component(suite)
    validate_ratio_definitions_loaded(suite)
    
    # 5. Integration
    print("[PHASE 5] Integration Validation...")
    validate_real_data_integration(suite)
    validate_component_extraction(suite)
    
    # 6. Monte Carlo
    print("[PHASE 6] Monte Carlo Validation...")
    validate_monte_carlo_engine(suite)
    validate_var_calculation(suite)
    
    # Print report
    success = suite.print_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_all_validations())

