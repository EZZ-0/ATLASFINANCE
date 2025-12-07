"""
UI Components Package
=====================
Reusable UI components for ATLAS Financial Intelligence.

Components:
- draggable_grid: Drag-and-drop dashboard layout (M014 - Executor)
- mobile_responsive: CSS and helpers for responsive design (M015)
"""

from .draggable_grid import (
    render_draggable_metrics,
    render_reorder_controls,
    get_ordered_metrics,
    get_layout_order,
    save_layout_order,
    reset_layout,
    inject_drag_styles,
    GridConfig,
    DEFAULT_METRIC_ORDER,
    METRIC_NAMES,
    SORTABLES_AVAILABLE
)

from .mobile_responsive import (
    inject_responsive_css,
    get_device_type,
    responsive_columns,
    collapsible_on_mobile,
    mobile_friendly_button,
    inject_viewport_meta,
    BREAKPOINTS
)

__all__ = [
    # Draggable Grid (M014)
    'render_draggable_metrics',
    'render_reorder_controls', 
    'get_ordered_metrics',
    'get_layout_order',
    'save_layout_order',
    'reset_layout',
    'inject_drag_styles',
    'GridConfig',
    'DEFAULT_METRIC_ORDER',
    'METRIC_NAMES',
    'SORTABLES_AVAILABLE',
    # Mobile Responsive (M015)
    'inject_responsive_css',
    'get_device_type',
    'responsive_columns',
    'collapsible_on_mobile',
    'mobile_friendly_button',
    'inject_viewport_meta',
    'BREAKPOINTS'
]
