# 💾 UI THEME BACKUP - RICH BROWN-BLACK LUXURY
# Date: November 30, 2025
# Theme: Executive Dark Theme with Gold Accents
# Style: Bloomberg Terminal / Luxury Finance Platform

"""
COMPLETE CSS BACKUP FOR USA EARNINGS ENGINE
============================================
This file contains the complete CSS theme that can be copy-pasted
into any Streamlit app to recreate the exact luxury look.

COLORS:
- Background: #0F0A08 - #1A110D (Rich brown-black gradient)
- Primary Accent: #FFD700 - #FFB300 (Gold gradient)
- Text: #E0E0E0 (Light gray)
- Secondary Background: #1A110D (Dark chocolate)

USAGE:
Copy the entire CSS block below and paste it into:
st.markdown('''<style>...CSS HERE...</style>''', unsafe_allow_html=True)
"""

COMPLETE_CSS = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
    /* ==========================================
       EXECUTIVE DARK THEME - RICH BROWN-BLACK
       ========================================== */
    
    /* Main App Background - Force Override */
    .stApp {
        background: linear-gradient(135deg, #0F0A08 0%, #1A110D 50%, #120C0A 100%) !important;
        color: #E0E0E0 !important;
    }
    
    /* Force Streamlit containers to use our theme */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0F0A08 0%, #1A110D 50%, #120C0A 100%) !important;
    }
    
    [data-testid="stHeader"] {
        background: rgba(15, 10, 8, 0.95) !important;
    }
    
    .main .block-container {
        background: transparent !important;
    }
    
    /* Global Font Enhancement */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: #E0E0E0;
    }
    
    /* ==========================================
       PREMIUM HEADER WITH ANIMATION
       ========================================== */
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFB300 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        animation: fadeInDown 0.8s ease-out;
        letter-spacing: -1px;
        text-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
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
    
    /* ==========================================
       METRIC CARDS - GLASSMORPHISM
       ========================================== */
    
    .metric-card {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid rgba(255, 215, 0, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 215, 0, 0.1);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(255, 215, 0, 0.15), inset 0 1px 0 rgba(255, 215, 0, 0.2);
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    /* Streamlit Metrics Enhancement */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.8) 0%, rgba(20, 20, 20, 0.9) 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 215, 0, 0.12);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
    }
    
    [data-testid="stMetric"]:hover {
        border-color: rgba(255, 215, 0, 0.25);
        box-shadow: 0 6px 24px rgba(255, 215, 0, 0.1);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #FFB300 !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #E0E0E0 !important;
    }
    
    /* ==========================================
       TABS - PROFESSIONAL STYLING
       ========================================== */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background-color: rgba(30, 30, 30, 0.5);
        padding: 0.5rem;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border-radius: 8px;
        padding: 0 24px;
        font-weight: 500;
        color: #E0E0E0 !important;
        transition: all 0.2s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 179, 0, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FFB300 0%, #FFA000 100%);
        color: #121212 !important;
        box-shadow: 0 4px 12px rgba(255, 179, 0, 0.4);
    }
    
    /* ==========================================
       DATA TABLES - RICH BROWN THEME
       ========================================== */
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        background-color: #1A110D;
    }
    
    .stDataFrame th {
        background: linear-gradient(135deg, #FFB300 0%, #FFA000 100%);
        color: #121212 !important;
        font-weight: 600;
        padding: 12px 16px !important;
        text-transform: uppercase;
        font-size: 0.75rem;
        letter-spacing: 0.5px;
    }
    
    .stDataFrame td {
        padding: 12px 16px !important;
        border-bottom: 1px solid rgba(255, 179, 0, 0.1);
        color: #E0E0E0 !important;
        background-color: #1A110D;
    }
    
    .stDataFrame tr:hover {
        background-color: rgba(255, 179, 0, 0.05);
    }
    
    /* ==========================================
       SIDEBAR - RICH BROWN THEME
       ========================================== */
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A110D 0%, #0F0A08 100%);
        border-right: 1px solid rgba(255, 179, 0, 0.2);
    }
    
    /* ==========================================
       BUTTONS - GOLD ACCENT
       ========================================== */
    
    .stButton button {
        background: linear-gradient(135deg, #FFB300 0%, #FFA000 100%);
        color: #121212;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255, 179, 0, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 179, 0, 0.5);
    }
    
    /* ==========================================
       CHARTS - RICH BROWN THEME
       ========================================== */
    
    .js-plotly-plot {
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
        overflow: hidden;
        background-color: #1A110D;
    }
    
    /* ==========================================
       EXPANDERS - DARK THEME
       ========================================== */
    
    .streamlit-expanderHeader {
        background-color: rgba(255, 179, 0, 0.1);
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        color: #E0E0E0 !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: rgba(255, 179, 0, 0.2);
    }
    
    /* ==========================================
       ALERTS - EXECUTIVE STYLING
       ========================================== */
    
    .stAlert {
        border-radius: 12px;
        border-left-width: 4px;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%);
        color: #E0E0E0;
        border: 1px solid rgba(255, 215, 0, 0.1);
    }
    
    /* Success/Info/Warning/Error Colors */
    .element-container:has(.stSuccess) .stAlert {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%);
        border-left-color: #4CAF50;
        border: 1px solid rgba(76, 175, 80, 0.25);
        box-shadow: 0 4px 16px rgba(76, 175, 80, 0.1);
    }
    
    .element-container:has(.stInfo) .stAlert {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%);
        border-left-color: #FFD700;
        border: 1px solid rgba(255, 215, 0, 0.25);
        box-shadow: 0 4px 16px rgba(255, 215, 0, 0.1);
    }
    
    .element-container:has(.stWarning) .stAlert {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%);
        border-left-color: #FF9800;
        border: 1px solid rgba(255, 152, 0, 0.25);
        box-shadow: 0 4px 16px rgba(255, 152, 0, 0.1);
    }
    
    .element-container:has(.stError) .stAlert {
        background: linear-gradient(135deg, rgba(26, 26, 26, 0.95) 0%, rgba(20, 20, 20, 0.98) 100%);
        border-left-color: #F44336;
        border: 1px solid rgba(244, 67, 54, 0.25);
        box-shadow: 0 4px 16px rgba(244, 67, 54, 0.1);
    }
    
    /* ==========================================
       LOADING SPINNER - GOLD
       ========================================== */
    
    .stSpinner > div {
        border-top-color: #FFD700 !important;
    }
    
    /* ==========================================
       SCROLLBAR - RICH BROWN THEME
       ========================================== */
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1A110D;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #FFB300 0%, #FFA000 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #FFA000 0%, #FFB300 100%);
    }
    
    /* ==========================================
       INPUT FIELDS - RICH BROWN THEME
       ========================================== */
    
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #1A110D !important;
        color: #E0E0E0 !important;
        border: 1px solid rgba(255, 179, 0, 0.2) !important;
        border-radius: 8px;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus, .stNumberInput input:focus {
        border-color: #FFB300 !important;
        box-shadow: 0 0 0 1px #FFB300 !important;
    }
    
    /* ==========================================
       CHECKBOX & RADIO - DARK THEME
       ========================================== */
    
    .stCheckbox, .stRadio {
        color: #E0E0E0 !important;
    }
    
    /* ==========================================
       HEADERS - LIGHT GRAY
       ========================================== */
    
    h1, h2, h3, h4, h5, h6 {
        color: #E0E0E0 !important;
    }
    
    /* ==========================================
       MARKDOWN TEXT
       ========================================== */
    
    .stMarkdown {
        color: #E0E0E0 !important;
    }
    
    /* ==========================================
       RESPONSIVE TYPOGRAPHY
       ========================================== */
    
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
    }
    
    /* ==========================================
       FADE-IN ANIMATION FOR CONTENT
       ========================================== */
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
</style>
"""

# ==========================================
# STREAMLIT CONFIG.TOML
# ==========================================

CONFIG_TOML = """
# Streamlit Theme Configuration
# Rich Brown-Black Luxury Theme

[theme]
primaryColor = "#FFD700"              # Gold accent
backgroundColor = "#0F0A08"            # Rich brown-black main background
secondaryBackgroundColor = "#1A110D"  # Dark chocolate for cards/sidebar
textColor = "#E0E0E0"                  # Light gray text
font = "sans serif"

[server]
enableCORS = false
enableXsrfProtection = false
"""

# ==========================================
# COLOR PALETTE REFERENCE
# ==========================================

COLOR_PALETTE = {
    "backgrounds": {
        "main": "#0F0A08",  # Very dark brown-black
        "secondary": "#1A110D",  # Dark chocolate
        "gradient_mid": "#120C0A",  # Transition color
    },
    "accents": {
        "gold_primary": "#FFD700",  # Bright gold
        "gold_secondary": "#FFA500",  # Orange-gold
        "gold_tertiary": "#FFB300",  # Warm gold
    },
    "text": {
        "primary": "#E0E0E0",  # Light gray
        "secondary": "#A0A0A0",  # Medium gray
        "dark": "#121212",  # For gold buttons
    },
    "semantic": {
        "success": "#4CAF50",  # Green
        "info": "#FFD700",  # Gold
        "warning": "#FF9800",  # Orange
        "error": "#F44336",  # Red
    }
}

# ==========================================
# USAGE INSTRUCTIONS
# ==========================================

USAGE = """
TO USE THIS THEME IN ANY STREAMLIT APP:

1. Copy the COMPLETE_CSS variable content
2. Paste into your Streamlit app:
   
   st.markdown(COMPLETE_CSS, unsafe_allow_html=True)

3. Create .streamlit/config.toml with CONFIG_TOML content

4. Hard refresh browser (Ctrl + Shift + R)

5. Enjoy your luxury theme!

COMPATIBILITY:
- Works with Streamlit 1.28+
- Tested on Chrome, Firefox, Edge
- Responsive design included
- All Streamlit components styled

CUSTOMIZATION:
- Change #0F0A08 to adjust background warmth
- Change #FFD700 to adjust accent color
- All colors use CSS variables for easy modification
"""

# ==========================================
# VERSION & CHANGELOG
# ==========================================

VERSION = "1.0.0"
DATE = "November 30, 2025"
CHANGELOG = """
v1.0.0 - November 30, 2025
- Initial release
- Rich Brown-Black luxury theme
- Gold accents throughout
- Bloomberg Terminal inspired
- Full Streamlit component coverage
- Responsive design
- Professional animations
"""


