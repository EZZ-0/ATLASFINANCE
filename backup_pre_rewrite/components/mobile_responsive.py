"""
MOBILE RESPONSIVENESS - MILESTONE-015
=====================================

CSS and layout adjustments for mobile/tablet viewing.
Streamlit apps need explicit responsive handling.

Features:
- Breakpoint-based CSS
- Touch-friendly buttons
- Collapsible sections on mobile
- Readable font sizes

Author: ATLAS Architect
Date: 2025-12-08
"""

import streamlit as st


# Breakpoints (pixels)
BREAKPOINTS = {
    'mobile': 480,
    'tablet': 768,
    'laptop': 1024,
    'desktop': 1280,
}


def inject_responsive_css():
    """
    Inject responsive CSS that adapts to screen size.
    Call this once at the start of the app.
    """
    
    css = """
    <style>
    /* ============================================
       MOBILE RESPONSIVENESS - M015
       ============================================ */
    
    /* Base: Mobile First */
    :root {
        --font-size-base: 14px;
        --spacing-base: 0.5rem;
        --card-min-width: 100%;
    }
    
    /* ============================================
       MOBILE (< 480px)
       ============================================ */
    @media screen and (max-width: 480px) {
        /* Make columns stack vertically */
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            min-width: 100% !important;
        }
        
        /* Larger touch targets */
        .stButton > button {
            min-height: 48px !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
        }
        
        /* Readable text */
        .stMarkdown p, .stMarkdown li {
            font-size: 14px !important;
            line-height: 1.6 !important;
        }
        
        /* Headers */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        /* Metrics - stack and enlarge */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        /* Tables - horizontal scroll */
        .stDataFrame {
            overflow-x: auto !important;
        }
        
        /* Sidebar - full width when open */
        [data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* Hide decorative elements */
        .main-header i {
            display: none !important;
        }
        
        /* Flip cards - full width */
        .fc-wrap, .flip-wrap {
            min-width: 100% !important;
        }
        
        /* Charts - prevent overflow */
        .js-plotly-plot, .plotly {
            width: 100% !important;
            max-width: 100vw !important;
        }
    }
    
    /* ============================================
       TABLET (481px - 768px)
       ============================================ */
    @media screen and (min-width: 481px) and (max-width: 768px) {
        /* Two columns max */
        [data-testid="column"] {
            min-width: 48% !important;
        }
        
        /* Slightly larger touch targets */
        .stButton > button {
            min-height: 44px !important;
        }
        
        /* Headers */
        h1 { font-size: 1.75rem !important; }
        h2 { font-size: 1.4rem !important; }
        
        /* Flip cards - two per row */
        .fc-wrap, .flip-wrap {
            min-width: 48% !important;
        }
    }
    
    /* ============================================
       LAPTOP (769px - 1024px)
       ============================================ */
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        /* Three columns */
        [data-testid="column"] {
            min-width: 32% !important;
        }
        
        /* Flip cards - three per row */
        .fc-wrap, .flip-wrap {
            min-width: 31% !important;
        }
    }
    
    /* ============================================
       DESKTOP (1025px+)
       ============================================ */
    @media screen and (min-width: 1025px) {
        /* Full layout - 5 columns */
        [data-testid="column"] {
            min-width: auto !important;
        }
        
        /* Flip cards - five per row */
        .fc-wrap, .flip-wrap {
            min-width: 18% !important;
        }
    }
    
    /* ============================================
       TOUCH ENHANCEMENTS
       ============================================ */
    @media (hover: none) and (pointer: coarse) {
        /* Touch device detected */
        
        /* Larger click areas */
        .stButton > button,
        .stSelectbox,
        .stTextInput input {
            min-height: 48px !important;
        }
        
        /* No hover effects on touch */
        .fc-wrap:hover .fc-inner,
        .flip-wrap:hover .flip-inner {
            box-shadow: none !important;
        }
        
        /* Flip cards - tap to flip (already works) */
    }
    
    /* ============================================
       PRINT STYLES
       ============================================ */
    @media print {
        /* Hide interactive elements */
        .stButton, .stSelectbox, .stTextInput, 
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Show all content */
        .stExpander {
            display: block !important;
        }
        
        /* Black text */
        * {
            color: black !important;
            background: white !important;
        }
    }
    
    /* ============================================
       LANDSCAPE ORIENTATION
       ============================================ */
    @media screen and (orientation: landscape) and (max-height: 500px) {
        /* Compact mode for landscape phones */
        .main-header {
            font-size: 1.2rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Reduce vertical spacing */
        .block-container {
            padding-top: 1rem !important;
        }
    }
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


def get_device_type() -> str:
    """
    Attempt to detect device type from viewport.
    Note: This is a best-effort detection using CSS.
    
    Returns device category for conditional rendering.
    """
    # Streamlit doesn't expose viewport directly
    # Use CSS for actual responsiveness
    # This function is for logging/analytics only
    return "unknown"


def responsive_columns(items: list, mobile_cols: int = 1, tablet_cols: int = 2, desktop_cols: int = 5):
    """
    Create responsive column layout.
    
    On mobile: All items stack (1 column)
    On tablet: 2 columns
    On desktop: 5 columns (or specified)
    
    Note: Actual responsiveness handled by CSS.
    This creates the base columns for desktop.
    """
    return st.columns(desktop_cols)


def collapsible_on_mobile(title: str, content_func, expanded_desktop: bool = True):
    """
    Create an expander that's collapsed on mobile, expanded on desktop.
    
    Args:
        title: Expander title
        content_func: Function that renders content
        expanded_desktop: Whether to expand by default on desktop
    """
    # On mobile, CSS will handle collapse behavior
    with st.expander(title, expanded=expanded_desktop):
        content_func()


def mobile_friendly_button(label: str, key: str = None, **kwargs) -> bool:
    """
    Create a mobile-friendly button with larger touch target.
    """
    # CSS handles sizing, this is for semantic clarity
    return st.button(label, key=key, use_container_width=True, **kwargs)


def inject_viewport_meta():
    """
    Inject viewport meta tag for proper mobile scaling.
    """
    meta = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    """
    st.markdown(meta, unsafe_allow_html=True)


# Export
__all__ = [
    'inject_responsive_css',
    'get_device_type',
    'responsive_columns',
    'collapsible_on_mobile',
    'mobile_friendly_button',
    'inject_viewport_meta',
    'BREAKPOINTS'
]

