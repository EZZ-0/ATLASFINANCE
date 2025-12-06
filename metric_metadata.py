"""
METRIC METADATA MODULE
======================
Provides data provenance tracking for all extracted financial metrics.

Every metric can be wrapped with metadata that includes:
- Source (SEC, yfinance, calculated)
- Extraction timestamp
- Period covered (TTM, FY2024, Q3 2024, etc.)
- Confidence score
- Raw vs formatted values

Usage:
    from metric_metadata import MetricMetadata, wrap_metric, create_metric_with_provenance
    
    # Simple usage
    pe_ratio = MetricMetadata(
        value=28.5,
        source="yfinance",
        timestamp="2025-12-03T10:30:00Z",
        period="TTM",
        confidence=0.95
    )
    
    # Access value
    print(f"P/E: {pe_ratio.value}")
    
    # Get full details
    print(pe_ratio.to_dict())
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, Union
import json


@dataclass
class MetricMetadata:
    """
    Container for a metric value with full provenance tracking.
    
    Attributes:
        value: The actual metric value (can be float, int, or str)
        source: Data source ("yfinance", "sec", "calculated", "manual")
        timestamp: When the data was extracted (ISO format)
        period: Period the metric covers ("TTM", "FY2024", "Q3 2024", etc.)
        confidence: Confidence score 0.0-1.0
        raw_value: Original unformatted value (if different from value)
        calculation_method: How the metric was calculated (if applicable)
        discrepancy_warning: Warning if values don't match between sources
        notes: Additional notes or context
    """
    value: Union[float, int, str, None]
    source: str = "unknown"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    period: str = "unknown"
    confidence: float = 1.0
    raw_value: Optional[Union[float, int, str]] = None
    calculation_method: Optional[str] = None
    discrepancy_warning: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate confidence score is within bounds"""
        if self.confidence < 0.0:
            self.confidence = 0.0
        elif self.confidence > 1.0:
            self.confidence = 1.0
        
        # Set raw_value to value if not provided
        if self.raw_value is None:
            self.raw_value = self.value
    
    def __float__(self) -> float:
        """Allow MetricMetadata to be used as a float"""
        if isinstance(self.value, (int, float)):
            return float(self.value)
        return 0.0
    
    def __int__(self) -> int:
        """Allow MetricMetadata to be used as an int"""
        if isinstance(self.value, (int, float)):
            return int(self.value)
        return 0
    
    def __str__(self) -> str:
        """String representation shows value with source indicator"""
        if self.value is None:
            return "N/A"
        return f"{self.value}"
    
    def __repr__(self) -> str:
        return f"MetricMetadata({self.value}, source={self.source}, period={self.period}, confidence={self.confidence:.0%})"
    
    def is_stale(self, hours: int = 24) -> bool:
        """Check if the metric data is stale (older than specified hours)"""
        try:
            extracted_time = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
            age = datetime.now(extracted_time.tzinfo) - extracted_time
            return age.total_seconds() > (hours * 3600)
        except (ValueError, TypeError):
            return True  # Assume stale if timestamp is invalid
    
    def get_confidence_label(self) -> str:
        """Get human-readable confidence label"""
        if self.confidence >= 0.95:
            return "Very High"
        elif self.confidence >= 0.80:
            return "High"
        elif self.confidence >= 0.60:
            return "Moderate"
        elif self.confidence >= 0.40:
            return "Low"
        else:
            return "Very Low"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "value": self.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "period": self.period,
            "confidence": self.confidence,
            "confidence_label": self.get_confidence_label(),
            "raw_value": self.raw_value,
            "calculation_method": self.calculation_method,
            "discrepancy_warning": self.discrepancy_warning,
            "notes": self.notes,
            "is_stale": self.is_stale()
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MetricMetadata':
        """Create MetricMetadata from dictionary"""
        return cls(
            value=data.get('value'),
            source=data.get('source', 'unknown'),
            timestamp=data.get('timestamp', datetime.now().isoformat()),
            period=data.get('period', 'unknown'),
            confidence=data.get('confidence', 1.0),
            raw_value=data.get('raw_value'),
            calculation_method=data.get('calculation_method'),
            discrepancy_warning=data.get('discrepancy_warning'),
            notes=data.get('notes')
        )


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def wrap_metric(
    value: Union[float, int, str, None],
    source: str = "calculated",
    period: str = "latest",
    confidence: float = 0.80
) -> MetricMetadata:
    """
    Quick helper to wrap a value with basic metadata.
    
    Args:
        value: The metric value
        source: Data source
        period: Time period
        confidence: Confidence score
    
    Returns:
        MetricMetadata instance
    """
    return MetricMetadata(
        value=value,
        source=source,
        timestamp=datetime.now().isoformat(),
        period=period,
        confidence=confidence
    )


def create_metric_with_provenance(
    value: Union[float, int, str, None],
    source: str,
    period: str,
    calculation_method: Optional[str] = None,
    market_value: Optional[float] = None,
    confidence: float = 0.90
) -> MetricMetadata:
    """
    Create a metric with full provenance tracking, including
    comparison with market value if available.
    
    Args:
        value: Calculated or extracted value
        source: Data source
        period: Time period
        calculation_method: How it was calculated
        market_value: Value from market data source (for comparison)
        confidence: Base confidence score
    
    Returns:
        MetricMetadata with discrepancy warning if values differ
    """
    discrepancy_warning = None
    
    # Check for discrepancy with market value
    if market_value is not None and value is not None:
        try:
            value_float = float(value)
            market_float = float(market_value)
            
            if market_float != 0:
                diff_pct = abs(value_float - market_float) / abs(market_float)
                
                if diff_pct > 0.15:  # More than 15% difference
                    discrepancy_warning = (
                        f"Calculated value ({value_float:.2f}) differs from "
                        f"market value ({market_float:.2f}) by {diff_pct:.1%}"
                    )
                    # Reduce confidence due to discrepancy
                    confidence = max(0.5, confidence - 0.2)
        except (ValueError, TypeError):
            pass
    
    return MetricMetadata(
        value=value,
        source=source,
        timestamp=datetime.now().isoformat(),
        period=period,
        confidence=confidence,
        calculation_method=calculation_method,
        discrepancy_warning=discrepancy_warning
    )


def unwrap_metric(metric: Union[MetricMetadata, float, int, str, None]) -> Union[float, int, str, None]:
    """
    Safely extract the value from a metric (works with both wrapped and unwrapped values).
    
    Args:
        metric: Either a MetricMetadata instance or raw value
    
    Returns:
        The raw value
    """
    if isinstance(metric, MetricMetadata):
        return metric.value
    return metric


def get_metric_source(metric: Union[MetricMetadata, Any]) -> str:
    """
    Get the source of a metric (or "unknown" for unwrapped values).
    
    Args:
        metric: Either a MetricMetadata instance or raw value
    
    Returns:
        Source string
    """
    if isinstance(metric, MetricMetadata):
        return metric.source
    return "unknown"


# ==========================================
# CONFIDENCE SCORING GUIDELINES
# ==========================================

CONFIDENCE_GUIDELINES = {
    "direct_api": 0.95,      # Direct pull from yfinance/SEC API
    "calculated_reliable": 0.85,  # Calculated from reliable source data
    "calculated_mixed": 0.70,     # Calculated from mixed sources
    "fuzzy_extraction": 0.55,     # Fuzzy/heuristic extraction
    "default_fallback": 0.30,     # Using default/fallback values
    "manual_input": 0.80,         # User-provided values
}


# ==========================================
# EXAMPLE USAGE
# ==========================================

if __name__ == "__main__":
    print("=" * 80)
    print("METRIC METADATA - EXAMPLE USAGE")
    print("=" * 80)
    
    # Example 1: Simple metric
    pe_ratio = MetricMetadata(
        value=28.5,
        source="yfinance",
        period="TTM",
        confidence=0.95,
        calculation_method="trailingPE from Yahoo Finance"
    )
    
    print(f"\n1. P/E Ratio: {pe_ratio}")
    print(f"   Source: {pe_ratio.source}")
    print(f"   Confidence: {pe_ratio.get_confidence_label()} ({pe_ratio.confidence:.0%})")
    print(f"   Stale: {pe_ratio.is_stale()}")
    
    # Example 2: Calculated metric with discrepancy
    roe = create_metric_with_provenance(
        value=0.147,
        source="calculated",
        period="FY2024",
        calculation_method="Net Income / Shareholders Equity",
        market_value=0.152,
        confidence=0.85
    )
    
    print(f"\n2. ROE: {float(roe):.1%}")
    print(f"   Discrepancy: {roe.discrepancy_warning or 'None'}")
    
    # Example 3: Using as numeric
    debt_equity = wrap_metric(1.96, source="yfinance", period="Q3 2024")
    
    # Can use in calculations
    leverage_factor = float(debt_equity) * 2
    print(f"\n3. D/E Ratio: {debt_equity}")
    print(f"   Leverage Factor (D/E × 2): {leverage_factor}")
    
    # Example 4: JSON export
    print(f"\n4. Full metadata (JSON):")
    print(pe_ratio.to_json())
    
    print("\n" + "=" * 80)






