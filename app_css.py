"""
APP CSS - Centralized Styling Module
=====================================
All CSS for the ATLAS Financial Intelligence app.
Extracted from usa_app.py for maintainability.

Usage:
    from app_css import inject_all_css, get_background_css
    inject_all_css()  # Call once at app start
"""

import streamlit as st
import os
import base64


def get_main_theme_css() -> str:
    """
    Main theme CSS - Professional Financial Dark Theme
    ~500 lines of core styling
    """
    return """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" media="print" onload="this.media='all'">
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
<noscript>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
</noscript>
<style>
    /* Material Symbols for ALL Streamlit icon elements */
    .material-symbols-rounded,
    [data-testid="stIconMaterial"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] span,
    button[kind="header"] span {
        font-family: 'Material Symbols Rounded' !important;
        font-weight: normal;
        font-style: normal;
        font-size: 24px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: 'liga';
        font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
    }
    
    /* Force Material Symbols on icon spans showing text */
    span[data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
        font-size: 24px !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-feature-settings: 'liga' 1 !important;
        text-rendering: optimizeLegibility !important;
    }
    
    /* Hide sidebar toggle entirely if icons don't render - use CSS alternative */
    [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"],
    [data-testid="collapsedControl"] span[data-testid="stIconMaterial"] {
        font-size: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] span[data-testid="stIconMaterial"]::after,
    [data-testid="collapsedControl"] span[data-testid="stIconMaterial"]::after {
        content: '◀' !important;
        font-size: 18px !important;
        font-family: system-ui, sans-serif !important;
    }
    [data-testid="collapsedControl"] span[data-testid="stIconMaterial"]::after {
        content: '▶' !important;
    }
    
    /* Professional Financial Dark Theme - Clean & Readable */
    :root {
        --bg-primary: #0f1419;
        --bg-secondary: #1a1f26;
        --bg-card: #1e2530;
        --bg-hover: #252d3a;
        --text-primary: #f0f4f8;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-primary: #3b82f6;
        --accent-secondary: #10b981;
        --accent-gold: #f59e0b;
        --border-subtle: rgba(148, 163, 184, 0.1);
        --border-accent: rgba(59, 130, 246, 0.3);
    }
    
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    
    /* Force Streamlit containers to use our theme */
    [data-testid="stAppViewContainer"] {
        background: var(--bg-primary) !important;
    }
    
    [data-testid="stHeader"] {
        background: rgba(15, 20, 25, 0.95) !important;
        backdrop-filter: blur(10px);
    }
    
    .main .block-container {
        background: transparent !important;
    }
    
    /* Global Font Enhancement */
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: var(--text-primary);
    }
    
    /* Premium Header with Animation */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: white !important;
        text-align: center;
        padding: 1.5rem 0;
        animation: fadeInDown 0.8s ease-out;
        letter-spacing: -1px;
        text-shadow: 0 0 30px rgba(59, 130, 246, 0.5), 
                     0 2px 4px rgba(0, 0, 0, 0.5);
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Clean Metric Cards - Solid, Readable Design */
    .metric-card {
        background: #1e2530 !important;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(59, 130, 246, 0.15);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        border-color: rgba(59, 130, 246, 0.3);
    }
    
    /* Streamlit Metrics - Clean Solid Design */
    [data-testid="stMetric"] {
        background: #1e2530 !important;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid rgba(59, 130, 246, 0.15);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(59, 130, 246, 0.3);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    /* Professional Tab Styling - Clean Solid Design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: #1a1f26 !important;
        padding: 0.5rem;
        border-radius: 10px;
        /* border removed - cleaner layout */
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 500;
        color: var(--text-secondary) !important;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: var(--bg-hover);
        color: var(--text-primary) !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #2563eb 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Enhanced Data Tables - Clean Solid Design */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        background-color: #1e2530 !important;
    }
    
    .stDataFrame th {
        background: #1a1f26 !important;
        color: var(--text-primary) !important;
        font-weight: 600;
        padding: 12px 16px !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
        border-bottom: 2px solid var(--accent-primary) !important;
    }
    
    .stDataFrame td {
        padding: 12px 16px !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        color: var(--text-primary) !important;
        background-color: #1e2530 !important;
    }
    
    .stDataFrame tr:hover {
        background-color: #252d3a !important;
    }
    
    /* Sidebar - Clean Solid Design with Overflow Fix */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f26 0%, #0f1419 100%) !important;
        border-right: 1px solid rgba(59, 130, 246, 0.12);
        overflow-x: hidden !important;
    }
    
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    
    /* CRITICAL: Fix sidebar text overflow when collapsed */
    [data-testid="stSidebar"][aria-expanded="false"] {
        overflow: hidden !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] * {
        visibility: hidden !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"][aria-expanded="false"] [data-testid="stSidebarCollapseButton"] * {
        visibility: visible !important;
    }
    
    /* Prevent text wrapping issues in sidebar */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] p {
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        max-width: 100% !important;
    }
    
    /* Sidebar Collapse Button - Clean Arrow Indicators */
    [data-testid="stSidebarCollapseButton"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-accent) !important;
        border-radius: 6px !important;
        width: 32px !important;
        height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        position: relative !important;
    }
    
    [data-testid="stSidebarCollapseButton"]:hover {
        background: var(--accent-primary) !important;
        border-color: var(--accent-primary) !important;
    }
    
    /* Use native SVG icon - style it properly */
    [data-testid="stSidebarCollapseButton"] svg {
        width: 18px !important;
        height: 18px !important;
        stroke: var(--text-primary) !important;
        stroke-width: 2.5 !important;
        fill: none !important;
    }
    
    [data-testid="stSidebarCollapseButton"]:hover svg {
        stroke: white !important;
    }
    
    /* Ensure sidebar collapse works on all platforms */
    [data-testid="stSidebar"][aria-expanded="false"] {
        transform: translateX(-100%) !important;
    }
    
    /* Hide any text content in collapse button (fallback for broken icons) */
    [data-testid="stSidebarCollapseButton"] span {
        font-size: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] span::before {
        font-size: 18px !important;
        content: '' !important;
    }
    
    /* Button Enhancements */
    .stButton button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, #2563eb 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
    }
    
    /* Charts Enhancement - Clean Solid Design */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        overflow: hidden;
        background-color: #1e2530 !important;
    }
    
    /* Expander Styling - Clean Solid Design */
    .streamlit-expanderHeader {
        background-color: #1a1f26 !important;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        color: var(--text-primary) !important;
        border: 1px solid rgba(59, 130, 246, 0.12);
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #252d3a !important;
        border-color: rgba(59, 130, 246, 0.25);
    }
    
    /* Metric Value Styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-primary) !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: var(--text-secondary) !important;
    }
    
    /* Positive/Negative deltas */
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Up"] ~ div {
        color: var(--accent-secondary) !important;
    }
    
    [data-testid="stMetricDelta"] svg[data-testid="stMetricDeltaIcon-Down"] ~ div {
        color: #ef4444 !important;
    }
    
    /* Alert Boxes - Clean Solid Design */
    .stAlert {
        border-radius: 10px;
        border-left-width: 4px;
        padding: 1rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        background: #1e2530 !important;
        color: var(--text-primary);
        border: 1px solid rgba(59, 130, 246, 0.12);
    }
    
    /* Loading Spinner */
    .stSpinner > div {
        border-top-color: var(--accent-primary) !important;
    }
    
    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 8px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-hover);
        border-radius: 8px;
        border: 2px solid var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-primary);
    }
    
    /* Input Fields */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Select box dropdown styling */
    [data-baseweb="select"] {
        background-color: var(--bg-secondary) !important;
    }
    
    [data-baseweb="select"] > div {
        background-color: var(--bg-secondary) !important;
        border-color: var(--border-subtle) !important;
    }
    
    [data-baseweb="popover"] {
        background-color: var(--bg-card) !important;
    }
    
    [data-baseweb="menu"] {
        background-color: var(--bg-card) !important;
    }
    
    [data-baseweb="menu"] li {
        background-color: var(--bg-card) !important;
    }
    
    [data-baseweb="menu"] li:hover {
        background-color: var(--bg-hover) !important;
    }
    
    /* Checkbox and Radio */
    .stCheckbox, .stRadio {
        color: var(--text-primary) !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
    
    /* Markdown Text */
    .stMarkdown {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: var(--text-primary) !important;
    }
    
    /* Success/Info/Warning/Error Messages */
    .element-container:has(.stSuccess) .stAlert {
        background: var(--bg-card);
        border-left-color: var(--accent-secondary) !important;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    
    .element-container:has(.stInfo) .stAlert {
        background: var(--bg-card);
        border-left-color: var(--accent-primary) !important;
        border: 1px solid rgba(59, 130, 246, 0.25);
    }
    
    .element-container:has(.stWarning) .stAlert {
        background: var(--bg-card);
        border-left-color: var(--accent-gold) !important;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    
    .element-container:has(.stError) .stAlert {
        background: var(--bg-card);
        border-left-color: #ef4444 !important;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }
    
    /* Responsive Typography */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
    }
    
    /* Fade-in Animation for Content */
    .element-container {
        animation: fadeIn 0.4s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    /* Table Grid Styling */
    [data-testid="stDataFrame"] .dvn-scroller {
        cursor: pointer !important;
    }
    
    [data-testid="stDataFrame"] div[role="grid"] {
        /* border removed - cleaner open layout */
        border-radius: 8px !important;
    }
    
    [data-testid="stDataFrame"] div[role="columnheader"],
    [data-testid="stDataFrame"] div[role="gridcell"] {
        border-right: none !important;
        border-bottom: 1px solid var(--border-subtle) !important;
    }
    
    /* Clean Alert Style */
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-left: 3px solid var(--accent-primary) !important;
        border-radius: 8px !important;
        padding: 1rem 1.5rem !important;
        color: var(--text-primary) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    }
    
    /* Alert types */
    .stAlert[kind="info"] {
        border-left-color: var(--accent-primary) !important;
    }
    
    .stAlert[kind="success"] {
        border-left-color: var(--accent-secondary) !important;
    }
    
    .stAlert[kind="warning"] {
        border-left-color: var(--accent-gold) !important;
    }
    
    .stAlert[kind="error"] {
        border-left-color: #ef4444 !important;
    }
    
    /* Number inputs and sliders */
    [data-testid="stNumberInput"] input {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    
    .stSlider > div > div > div {
        background-color: var(--accent-primary) !important;
    }
    
    /* Multiselect styling */
    .stMultiSelect > div > div {
        background-color: var(--bg-secondary) !important;
        border-color: var(--border-subtle) !important;
    }
    
    .stMultiSelect span[data-baseweb="tag"] {
        background-color: var(--accent-primary) !important;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-subtle) !important;
    }
    
    /* Caption and small text */
    .stCaption, small {
        color: var(--text-muted) !important;
    }
    
    /* Code blocks */
    code {
        background-color: var(--bg-secondary) !important;
        color: var(--accent-gold) !important;
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Divider */
    hr {
        border-color: var(--border-subtle) !important;
    }
    
    /* ==========================================
       CHROME IFRAME FIX (ECharts Gauges)
       Fixes Score Dashboard not appearing in Chrome
       ========================================== */
    
    /* Force iframe visibility for ECharts components */
    iframe {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
    }
    
    /* Ensure Streamlit custom components (ECharts) render properly */
    [data-testid="stCustomComponentV1"] {
        min-height: 200px !important;
        display: block !important;
        overflow: visible !important;
    }
    
    /* ECharts iframe specific styling */
    [data-testid="stCustomComponentV1"] iframe {
        background: transparent !important;
        border: none !important;
        outline: none !important;
        min-height: 200px !important;
        width: 100% !important;
    }
    
    /* All iframes - no borders */
    iframe {
        border: none !important;
        outline: none !important;
    }
    
    /* Gauge container fix */
    .element-container:has(iframe) {
        min-height: 200px;
        display: block !important;
        border: none !important;
        outline: none !important;
    }
</style>
"""


def get_background_css(bg_base64: str) -> str:
    """
    Background overlay CSS - World map with subtle opacity
    Requires base64 encoded image
    """
    return f"""
<style>
    /* ==========================================
       SUBTLE WORLD MAP OVERLAY
       To disable: Set ENABLE_BACKGROUND_IMAGE = False
       ========================================== */
    
    /* Keep original dark gradient as base */
    .stApp {{
        background: var(--bg-primary) !important;
        position: relative;
    }}
    
    [data-testid="stAppViewContainer"] {{
        background: var(--bg-primary) !important;
        position: relative;
    }}
    
    /* World map overlay with subtle opacity */
    [data-testid="stAppViewContainer"]::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: url("data:image/png;base64,{bg_base64}");
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        opacity: 0.22;
        pointer-events: none;
        z-index: 0;
    }}
    
    /* Ensure content stays above overlay */
    .main .block-container {{
        position: relative;
        z-index: 1;
    }}
    
    [data-testid="stSidebar"] {{
        position: relative;
        z-index: 1;
    }}
</style>
"""


def get_tab_scroll_css() -> str:
    """
    Tab scroll button and container CSS
    """
    return """
<style>
/* NOTE: Do NOT hide Streamlit's default buttons - they control sidebar */

/* Custom scroll buttons */
.scroll-btn {
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    z-index: 9999;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
}

.scroll-btn:hover {
    transform: translateY(-50%) scale(1.1);
    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

.scroll-btn-left {
    left: 15px;
}

.scroll-btn-right {
    right: 15px;
}

/* Tab scroll container enhancement - FIXED */
.stTabs [data-baseweb="tab-list"] {
    overflow-x: auto !important;
    overflow-y: hidden !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
    scroll-behavior: smooth;
    padding-bottom: 2px;
}

.stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
    display: none;
}

/* Ensure tabs don't wrap */
.stTabs [data-baseweb="tab"] {
    flex-shrink: 0 !important;
    white-space: nowrap !important;
}

/* Scroll indicators REMOVED - was causing dark borders on page edges */
/* .stTabs::before and ::after were creating the border effect */
</style>
"""


def get_header_button_css() -> str:
    """
    Header button matching CSS (New Search, AI Chat)
    """
    return """
<style>
/* Match header button styles */
div[data-testid="stHorizontalBlock"] .stButton button {
    font-size: 0.85rem !important;
    padding: 0.4rem 1rem !important;
    min-height: 38px !important;
    white-space: nowrap !important;
}
</style>
"""


def get_search_button_css() -> str:
    """
    Search button styling for sidebar
    """
    return """
<style>
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    padding: 0.8rem 2rem !important;
    font-size: 1.1rem !important;
    border-radius: 10px !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
    transition: all 0.3s ease !important;
}

div.stButton > button[kind="primary"]:hover {
    transform: translateY(-3px) scale(1.02) !important;
}
</style>
"""


def inject_all_css(enable_background: bool = True, bg_image_path: str = None):
    """
    Inject all CSS at once. Call this once at app start.
    
    Args:
        enable_background: Whether to enable the background image overlay
        bg_image_path: Path to background image file
    """
    # Main theme (always)
    st.markdown(get_main_theme_css(), unsafe_allow_html=True)
    
    # Background overlay (conditional)
    if enable_background and bg_image_path and os.path.exists(bg_image_path):
        with open(bg_image_path, "rb") as img_file:
            bg_base64 = base64.b64encode(img_file.read()).decode()
        st.markdown(get_background_css(bg_base64), unsafe_allow_html=True)
    
    # Tab scrolling
    st.markdown(get_tab_scroll_css(), unsafe_allow_html=True)
    
    # Header buttons
    st.markdown(get_header_button_css(), unsafe_allow_html=True)


# Export all functions
__all__ = [
    'get_main_theme_css',
    'get_background_css', 
    'get_tab_scroll_css',
    'get_header_button_css',
    'get_search_button_css',
    'inject_all_css'
]

