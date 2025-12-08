"""
Draggable Grid Component - MILESTONE-014
=========================================
Enables users to customize dashboard layout by reordering metric cards.

Uses streamlit-sortables when available, falls back to select-based reordering.

Created: 2025-12-08
Author: ATLAS Financial Intelligence (Executor)
"""

import streamlit as st
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass

# Try to import streamlit-sortables
try:
    from streamlit_sortables import sort_items
    SORTABLES_AVAILABLE = True
except ImportError:
    SORTABLES_AVAILABLE = False


# Default metric order
DEFAULT_METRIC_ORDER = [
    'PE_Ratio',
    'ROE', 
    'EV_EBITDA',
    'current_price',
    'market_cap',
    'Debt_Equity',
    'Net_Margin',
    'FCF_Yield',
    'Dividend_Yield',
    'Revenue_Growth'
]

# Metric display names
METRIC_NAMES = {
    'PE_Ratio': 'P/E Ratio',
    'ROE': 'Return on Equity',
    'EV_EBITDA': 'EV/EBITDA',
    'current_price': 'Stock Price',
    'market_cap': 'Market Cap',
    'Debt_Equity': 'Debt/Equity',
    'Net_Margin': 'Net Margin',
    'FCF_Yield': 'FCF Yield',
    'Dividend_Yield': 'Dividend Yield',
    'Revenue_Growth': 'Revenue Growth'
}


@dataclass
class GridConfig:
    """Configuration for the draggable grid."""
    columns: int = 5
    show_reorder_controls: bool = True
    persist_layout: bool = True
    layout_key: str = 'dashboard_layout'


def get_layout_order(config: GridConfig = None) -> List[str]:
    """
    Get the current layout order from session state.
    
    Returns:
        List of metric keys in current order
    """
    if config is None:
        config = GridConfig()
    
    if config.layout_key not in st.session_state:
        st.session_state[config.layout_key] = DEFAULT_METRIC_ORDER.copy()
    
    return st.session_state[config.layout_key]


def save_layout_order(order: List[str], config: GridConfig = None):
    """
    Save the layout order to session state.
    
    Args:
        order: New metric order
        config: Grid configuration
    """
    if config is None:
        config = GridConfig()
    
    st.session_state[config.layout_key] = order


def reset_layout(config: GridConfig = None):
    """Reset layout to default order."""
    if config is None:
        config = GridConfig()
    
    st.session_state[config.layout_key] = DEFAULT_METRIC_ORDER.copy()


def render_reorder_controls(config: GridConfig = None) -> Optional[List[str]]:
    """
    Render controls for reordering metrics.
    
    Returns:
        New order if changed, None otherwise
    """
    if config is None:
        config = GridConfig()
    
    current_order = get_layout_order(config)
    
    with st.expander("⚙️ Customize Dashboard Layout", expanded=False):
        st.markdown("**Drag metrics to reorder, or use the dropdowns below:**")
        
        # If sortables available, use it
        if SORTABLES_AVAILABLE:
            display_items = [METRIC_NAMES.get(m, m) for m in current_order]
            sorted_display = sort_items(display_items, direction="horizontal")
            
            # Map back to keys
            name_to_key = {v: k for k, v in METRIC_NAMES.items()}
            new_order = [name_to_key.get(name, name) for name in sorted_display]
            
            if new_order != current_order:
                save_layout_order(new_order, config)
                return new_order
        else:
            # Fallback: Use multiselect for reordering
            st.markdown("*Tip: Remove and re-add items in your preferred order*")
            
            available_metrics = list(METRIC_NAMES.keys())
            display_names = [METRIC_NAMES.get(m, m) for m in current_order]
            
            # Show current order with ability to change
            col1, col2 = st.columns([3, 1])
            
            with col1:
                selected = st.multiselect(
                    "Visible Metrics (order matters):",
                    options=[METRIC_NAMES.get(m, m) for m in available_metrics],
                    default=display_names,
                    key="metric_order_select"
                )
            
            with col2:
                if st.button("🔄 Reset", key="reset_layout_btn", help="Reset to default layout"):
                    reset_layout(config)
                    st.rerun()
            
            # Map back to keys
            if selected:
                name_to_key = {v: k for k, v in METRIC_NAMES.items()}
                new_order = [name_to_key.get(name, name) for name in selected]
                
                if new_order != current_order:
                    save_layout_order(new_order, config)
                    return new_order
        
        # Quick presets
        st.markdown("**Quick Presets:**")
        preset_col1, preset_col2, preset_col3 = st.columns(3)
        
        with preset_col1:
            if st.button("📊 Valuation Focus", key="preset_valuation"):
                save_layout_order([
                    'PE_Ratio', 'EV_EBITDA', 'current_price', 'market_cap',
                    'FCF_Yield', 'Dividend_Yield', 'ROE', 'Net_Margin',
                    'Debt_Equity', 'Revenue_Growth'
                ], config)
                st.rerun()
        
        with preset_col2:
            if st.button("💰 Income Focus", key="preset_income"):
                save_layout_order([
                    'Dividend_Yield', 'FCF_Yield', 'Net_Margin', 'ROE',
                    'current_price', 'PE_Ratio', 'Debt_Equity', 'EV_EBITDA',
                    'market_cap', 'Revenue_Growth'
                ], config)
                st.rerun()
        
        with preset_col3:
            if st.button("📈 Growth Focus", key="preset_growth"):
                save_layout_order([
                    'Revenue_Growth', 'ROE', 'Net_Margin', 'current_price',
                    'PE_Ratio', 'market_cap', 'EV_EBITDA', 'FCF_Yield',
                    'Dividend_Yield', 'Debt_Equity'
                ], config)
                st.rerun()
    
    return None


def render_draggable_metrics(
    financials: Dict[str, Any],
    render_metric_func: Callable[[str, Dict], None],
    config: GridConfig = None
):
    """
    Render metrics in a customizable grid layout.
    
    Args:
        financials: Financial data dictionary
        render_metric_func: Function to render individual metric card
        config: Grid configuration
    """
    if config is None:
        config = GridConfig()
    
    # Show reorder controls if enabled
    if config.show_reorder_controls:
        render_reorder_controls(config)
    
    # Get current order
    metric_order = get_layout_order(config)
    
    # Render metrics in grid
    cols = st.columns(config.columns)
    
    for idx, metric_key in enumerate(metric_order):
        with cols[idx % config.columns]:
            try:
                render_metric_func(metric_key, financials)
            except Exception as e:
                st.error(f"Error rendering {metric_key}: {str(e)}")


def get_ordered_metrics(config: GridConfig = None) -> List[str]:
    """
    Get the current ordered list of metrics.
    
    Returns:
        List of metric keys in current order
    """
    return get_layout_order(config)


# For CSS-based drag visual feedback (when sortables not available)
DRAG_STYLES = """
<style>
.draggable-metric {
    cursor: move;
    transition: transform 0.2s, box-shadow 0.2s;
}
.draggable-metric:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.draggable-metric:active {
    transform: scale(0.98);
    opacity: 0.8;
}
.layout-controls {
    background: var(--card-bg, rgba(26, 26, 46, 0.8));
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}
</style>
"""


def inject_drag_styles():
    """Inject CSS for drag visual feedback."""
    st.markdown(DRAG_STYLES, unsafe_allow_html=True)


# Test script
if __name__ == "__main__":
    st.set_page_config(page_title="Draggable Grid Test", layout="wide")
    
    st.title("Draggable Grid Component Test")
    
    # Inject styles
    inject_drag_styles()
    
    # Test data
    test_financials = {
        'pe_ratio': 25.5,
        'roe': 0.185,
        'ev_ebitda': 18.2,
        'current_price': 175.50,
        'market_cap': 2.8e12,
        'debt_equity': 1.2,
        'net_margin': 0.25,
        'fcf_yield': 0.035,
        'dividend_yield': 0.005,
        'revenue_growth': 0.08
    }
    
    # Simple render function for testing
    def test_render(metric_key: str, data: Dict):
        value = data.get(metric_key.lower(), "N/A")
        st.metric(METRIC_NAMES.get(metric_key, metric_key), str(value))
    
    # Render with controls
    config = GridConfig(columns=5, show_reorder_controls=True)
    render_draggable_metrics(test_financials, test_render, config)
    
    st.markdown("---")
    st.write("Current order:", get_ordered_metrics(config))
    st.write("Sortables available:", SORTABLES_AVAILABLE)

