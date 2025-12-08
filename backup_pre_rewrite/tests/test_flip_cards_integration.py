"""
FLIP CARDS INTEGRATION TESTS - MILESTONE-008
=============================================
Test flip cards render correctly across all tabs.

Author: ATLAS Architect
Created: 2025-12-08
"""

import pytest
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestFlipCardsModule:
    """Test the flip_cards.py module directly."""
    
    def test_import_flip_cards(self):
        """Verify flip_cards module imports successfully."""
        from flip_cards import (
            METRICS,
            render_flip_card,
            render_dashboard_metrics,
            render_valuation_metrics,
            get_metric_color,
            format_value
        )
        assert METRICS is not None
        assert len(METRICS) >= 20  # Should have 20+ metrics defined
    
    def test_metrics_have_required_fields(self):
        """All metrics should have required fields."""
        from flip_cards import METRICS
        
        required_fields = ['label', 'formula', 'insight', 'higher_is', 'unit', 'category']
        
        for key, config in METRICS.items():
            for field in required_fields:
                assert field in config, f"Metric {key} missing field: {field}"
    
    def test_color_logic_higher_is_better(self):
        """Test color logic for metrics where higher is better."""
        from flip_cards import get_metric_color
        
        # ROE benchmark is (10, 20), higher is better
        assert get_metric_color(25, "ROE") == "#10b981"  # Green - above high
        assert get_metric_color(15, "ROE") == "#f59e0b"  # Yellow - in range
        assert get_metric_color(5, "ROE") == "#ef4444"   # Red - below low
    
    def test_color_logic_higher_is_worse(self):
        """Test color logic for metrics where higher is worse."""
        from flip_cards import get_metric_color
        
        # Debt_to_Equity benchmark is (0.5, 1.5), higher is worse
        assert get_metric_color(0.3, "Debt_to_Equity") == "#10b981"  # Green - below low
        assert get_metric_color(1.0, "Debt_to_Equity") == "#f59e0b"  # Yellow - in range
        assert get_metric_color(2.0, "Debt_to_Equity") == "#ef4444"  # Red - above high
    
    def test_color_logic_neutral(self):
        """Test color logic for neutral metrics."""
        from flip_cards import get_metric_color
        
        # Beta benchmark is (0.8, 1.2), neutral
        assert get_metric_color(1.0, "Beta") == "#60a5fa"  # Blue - in range
        assert get_metric_color(0.5, "Beta") == "#f59e0b"  # Yellow - outside range
        assert get_metric_color(1.5, "Beta") == "#f59e0b"  # Yellow - outside range
    
    def test_format_value_dollar(self):
        """Test value formatting for dollar amounts."""
        from flip_cards import format_value
        
        formatted, num = format_value(1_500_000_000, "$")
        assert "$1.50B" in formatted
        
        formatted, num = format_value(500_000_000, "$")
        assert "M" in formatted or "B" in formatted
        
        formatted, num = format_value(None, "$")
        assert formatted == "N/A"
    
    def test_format_value_percent(self):
        """Test value formatting for percentages."""
        from flip_cards import format_value
        
        # Decimal input should be converted
        formatted, num = format_value(0.15, "%")
        assert "15" in formatted
        
        formatted, num = format_value(15.5, "%")
        assert "15.5%" in formatted
    
    def test_format_value_multiplier(self):
        """Test value formatting for multipliers (x)."""
        from flip_cards import format_value
        
        formatted, num = format_value(22.5, "x")
        assert "22.50x" in formatted
    
    def test_na_handling(self):
        """Test N/A handling for missing values."""
        from flip_cards import format_value, get_metric_color
        import pandas as pd
        
        # None
        formatted, num = format_value(None, "%")
        assert formatted == "N/A"
        assert num is None
        
        # NaN
        formatted, num = format_value(float('nan'), "%")
        assert formatted == "N/A"
        
        # Color for None
        color = get_metric_color(None, "ROE")
        assert color == "#6b7280"  # Gray


class TestDashboardTabIntegration:
    """Test dashboard_tab.py integration."""
    
    def test_dashboard_tab_imports(self):
        """Dashboard tab should import flip cards."""
        from dashboard_tab import FLIP_CARDS_AVAILABLE, METRICS
        assert FLIP_CARDS_AVAILABLE == True
        assert len(METRICS) >= 10


class TestMetricCoverage:
    """Verify all expected metrics are covered."""
    
    def test_valuation_metrics_exist(self):
        """Check valuation metrics defined."""
        from flip_cards import METRICS
        
        valuation = ["PE_Ratio", "PB_Ratio", "PS_Ratio", "EV_EBITDA", "FCF_Yield"]
        for m in valuation:
            assert m in METRICS, f"Missing valuation metric: {m}"
    
    def test_profitability_metrics_exist(self):
        """Check profitability metrics defined."""
        from flip_cards import METRICS
        
        profit = ["ROE", "ROA", "ROIC", "Gross_Margin", "Operating_Margin", "Net_Margin"]
        for m in profit:
            assert m in METRICS, f"Missing profitability metric: {m}"
    
    def test_alpha_signal_metrics_exist(self):
        """Check alpha signal metrics defined."""
        from flip_cards import METRICS
        
        alpha = ["Earnings_Momentum", "Insider_Sentiment", "Institutional_Flow"]
        for m in alpha:
            assert m in METRICS, f"Missing alpha metric: {m}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

