"""
DCF Input Validation Module
============================
Validates DCF assumptions to prevent invalid scenarios
"""

from typing import List, Tuple
from dcf_modeling import DCFAssumptions


class DCFValidationError(Exception):
    """Raised when DCF assumptions are invalid"""
    pass


def validate_dcf_assumptions(assumptions: DCFAssumptions) -> Tuple[List[str], List[str]]:
    """
    Validate DCF input assumptions
    
    Args:
        assumptions: DCFAssumptions dataclass
    
    Returns:
        Tuple of (errors, warnings)
        - errors: Critical issues that prevent calculation
        - warnings: Questionable values that should be reviewed
    
    Raises:
        DCFValidationError: If critical errors found
    """
    errors = []
    warnings = []
    
    # Revenue Growth Validation
    if assumptions.revenue_growth_rates:
        for i, growth in enumerate(assumptions.revenue_growth_rates):
            if not (-0.5 <= growth <= 2.0):
                errors.append(f"Year {i+1} revenue growth ({growth:.1%}) must be between -50% and 200%")
            elif growth > 0.5:
                warnings.append(f"Year {i+1} revenue growth ({growth:.1%}) >50% is very aggressive")
            elif growth < -0.2:
                warnings.append(f"Year {i+1} revenue growth ({growth:.1%}) <-20% indicates severe decline")
    
    # WACC (Discount Rate) Validation
    if not (0.01 <= assumptions.discount_rate <= 0.50):
        errors.append(f"WACC ({assumptions.discount_rate:.1%}) must be between 1% and 50%")
    elif assumptions.discount_rate < 0.05:
        warnings.append(f"WACC ({assumptions.discount_rate:.1%}) <5% is unusually low - verify calculation")
    elif assumptions.discount_rate > 0.25:
        warnings.append(f"WACC ({assumptions.discount_rate:.1%}) >25% is very high - implies extreme risk")
    
    # Terminal Growth Rate Validation
    if not (0 <= assumptions.terminal_growth_rate <= 0.10):
        errors.append(f"Terminal growth ({assumptions.terminal_growth_rate:.1%}) must be between 0% and 10%")
    elif assumptions.terminal_growth_rate > 0.05:
        warnings.append(f"Terminal growth ({assumptions.terminal_growth_rate:.1%}) >5% exceeds typical long-term GDP growth")
    elif assumptions.terminal_growth_rate > assumptions.discount_rate:
        errors.append(f"Terminal growth ({assumptions.terminal_growth_rate:.1%}) cannot exceed WACC ({assumptions.discount_rate:.1%})")
    
    # Tax Rate Validation
    if not (0 <= assumptions.tax_rate <= 0.50):
        errors.append(f"Tax rate ({assumptions.tax_rate:.1%}) must be between 0% and 50%")
    elif assumptions.tax_rate > 0.40:
        warnings.append(f"Tax rate ({assumptions.tax_rate:.1%}) >40% is unusually high")
    
    # CapEx % Revenue Validation
    if not (0 <= assumptions.capex_pct_revenue <= 0.50):
        errors.append(f"CapEx as % of revenue ({assumptions.capex_pct_revenue:.1%}) must be between 0% and 50%")
    elif assumptions.capex_pct_revenue > 0.30:
        warnings.append(f"CapEx ({assumptions.capex_pct_revenue:.1%}) >30% of revenue is capital-intensive")
    
    # Net Working Capital % Revenue Validation
    if not (-0.30 <= assumptions.nwc_pct_revenue <= 0.50):
        errors.append(f"NWC change as % of revenue ({assumptions.nwc_pct_revenue:.1%}) must be between -30% and 50%")
    
    # Depreciation % Revenue Validation
    if not (0 <= assumptions.depreciation_pct_revenue <= 0.30):
        errors.append(f"Depreciation as % of revenue ({assumptions.depreciation_pct_revenue:.1%}) must be between 0% and 30%")
    elif assumptions.depreciation_pct_revenue > 0.20:
        warnings.append(f"Depreciation ({assumptions.depreciation_pct_revenue:.1%}) >20% of revenue is unusual")
    
    # Projection Years Validation
    if not (1 <= assumptions.projection_years <= 15):
        errors.append(f"Projection years ({assumptions.projection_years}) must be between 1 and 15")
    elif assumptions.projection_years > 10:
        warnings.append(f"Projecting {assumptions.projection_years} years is very long-term and less reliable")
    
    # Cross-Validation Checks
    
    # Check if CapEx + NWC change is reasonable
    total_investment = assumptions.capex_pct_revenue + abs(assumptions.nwc_pct_revenue)
    if total_investment > 0.60:
        warnings.append(f"Total investment ({total_investment:.1%} of revenue) is very high - verify assumptions")
    
    # Check WACC vs terminal growth spread
    wacc_terminal_spread = assumptions.discount_rate - assumptions.terminal_growth_rate
    if wacc_terminal_spread < 0.02:
        errors.append(f"WACC-terminal growth spread ({wacc_terminal_spread:.1%}) <2% leads to unstable terminal value")
    
    # Raise exception if critical errors found
    if errors:
        error_msg = "DCF validation failed:\n" + "\n".join(f"  • {e}" for e in errors)
        raise DCFValidationError(error_msg)
    
    return errors, warnings


def validate_scenario_name(name: str) -> bool:
    """
    Validate scenario name for safe file operations
    
    Args:
        name: Scenario name
    
    Returns:
        True if valid, False otherwise
    """
    if not name or len(name) < 1:
        return False
    
    if len(name) > 50:
        return False
    
    # Check for invalid characters (path traversal, special chars)
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
    if any(char in name for char in invalid_chars):
        return False
    
    # Prevent reserved names
    reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'LPT1']
    if name.upper() in reserved:
        return False
    
    return True


# Example usage
if __name__ == "__main__":
    # Test validation
    from dcf_modeling import DCFAssumptions
    
    # Valid assumptions
    try:
        valid = DCFAssumptions(
            revenue_growth_rates=[0.10, 0.08, 0.06],
            terminal_growth_rate=0.03,
            discount_rate=0.10,
            tax_rate=0.21,
            capex_pct_revenue=0.05,
            nwc_pct_revenue=0.02,
            depreciation_pct_revenue=0.04,
            projection_years=5
        )
        errors, warnings = validate_dcf_assumptions(valid)
        print(f"✅ Valid assumptions: {len(warnings)} warnings")
        for w in warnings:
            print(f"  ⚠️ {w}")
    except DCFValidationError as e:
        print(f"❌ {e}")
    
    # Invalid assumptions
    try:
        invalid = DCFAssumptions(
            revenue_growth_rates=[0.10, 0.08, 0.06],
            terminal_growth_rate=0.12,  # Too high!
            discount_rate=0.10,
            tax_rate=0.21,
            capex_pct_revenue=0.05,
            nwc_pct_revenue=0.02,
            depreciation_pct_revenue=0.04,
            projection_years=5
        )
        errors, warnings = validate_dcf_assumptions(invalid)
    except DCFValidationError as e:
        print(f"\n❌ Invalid assumptions caught: {e}")

