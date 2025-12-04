"""
CENTRALIZED APPLICATION CONFIGURATION
======================================
Single source of truth for app branding, naming, and configuration.

This centralizes all hardcoded names/strings to make rebranding trivial.
"""

# ==========================================
# BRANDING
# ==========================================

APP_NAME = "ATLAS FINANCIAL INTELLIGENCE"
APP_NAME_SHORT = "Atlas Engine"
APP_TAGLINE = " Financial Analysis & Valuation Engine"
APP_VERSION = "2.0.0"
COMPANY_NAME = "Atlas Financial Intelligence"

# ==========================================
# VISUAL IDENTITY
# ==========================================

# Icon/Emoji (used in UI)
APP_ICON = "⚡"
AI_ICON = "🤖"
CHART_ICON = "📊"
REPORT_ICON = "📄"

# Theme colors (matches theme_presets.py)
PRIMARY_COLOR = "#3b82f6"  # Blue
SECONDARY_COLOR = "#10b981"  # Green accent
ACCENT_COLOR = "#f59e0b"  # Gold accent
BACKGROUND_DARK = "#0f1419"  # Clean dark charcoal
TEXT_PRIMARY = "#f0f4f8"  # Light gray for readability
TEXT_SECONDARY = "#94a3b8"  # Muted gray

# ==========================================
# FEATURE FLAGS
# ==========================================

FEATURES = {
    'ai_chat': True,  # AI chat feature (currently under maintenance)
    'live_dcf': True,  # Live DCF modeling
    'pdf_export': True,  # PDF report generation
    'investment_summary': True,  # Investment Summary tab
    'validation_engine': True,  # Data validation
    'quant_analysis': True,  # Fama-French quant engine
    'forensic_accounting': True,  # Forensic Shield
    'advanced_options': True,  # Developer/Advanced options
}

# ==========================================
# DATA SOURCES
# ==========================================

DATA_SOURCES = {
    'primary': 'SEC EDGAR',
    'secondary': 'Yahoo Finance',
    'news': 'Google News RSS',
    'options': 'Yahoo Finance Options Chain',
}

# ==========================================
# API CONFIGURATION
# ==========================================

# AI Models
AI_CONFIG = {
    'primary_model': 'gemini-2.0-flash-exp',
    'fallback_model': 'ollama/llama3.1',
    'temperature': 0.3,
    'max_tokens': 2000,
}

# Rate Limits (requests per minute)
RATE_LIMITS = {
    'sec_edgar': 10,  # SEC EDGAR API limit
    'yfinance': 2000,  # Unofficial limit (be conservative)
    'ai_requests': 60,  # Gemini free tier limit
}

# ==========================================
# FILE PATHS
# ==========================================

DIRECTORIES = {
    'logs': 'logs',
    'saved_scenarios': 'saved_scenarios',
    'exports': 'exports',
    'cache': '.cache',
}

# ==========================================
# UI CONFIGURATION
# ==========================================

UI_CONFIG = {
    'page_title': f"{APP_ICON} {APP_NAME}",
    'page_icon': APP_ICON,
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'menu_items': {
        'Get Help': None,
        'Report a bug': None,
        'About': f"""
        # {APP_ICON} {APP_NAME}
        
        {APP_TAGLINE}
        
        **Version:** {APP_VERSION}
        
        **Data Sources:**
        - SEC EDGAR (10-K, 10-Q filings)
        - Yahoo Finance (market data)
        - Google News (sentiment analysis)
        
        **Disclaimer:** This tool is for educational and research purposes only. 
        Not financial advice. Always do your own due diligence.
        """
    }
}

# ==========================================
# DISCLAIMERS & LEGAL
# ==========================================

DISCLAIMERS = {
    'main': """
    **⚠️ DISCLAIMER:** This tool is for educational and research purposes only. 
    The information provided does not constitute financial, investment, or professional advice. 
    Always consult with a qualified financial advisor before making investment decisions.
    """,
    'ai_chat': """
    **🔧 AI Chat is under development.**
    This feature uses experimental AI models and may produce inaccurate or incomplete responses.
    Always verify AI-generated insights with primary sources and professional analysis.
    """,
    'dcf_model': """
    **📊 DCF Model Assumptions:**
    All DCF valuations are based on assumptions about future performance. 
    Actual results may vary significantly. Adjust assumptions to reflect your own expectations.
    """,
    'forensic_accounting': """
    **🔍 Forensic Accounting:**
    These models detect patterns that may indicate financial distress or manipulation. 
    They are not definitive and should be used alongside human judgment and additional research.
    """
}

# ==========================================
# ANALYTICS
# ==========================================

ANALYTICS_CONFIG = {
    'enabled': True,  # Anonymous usage analytics
    'track_events': [
        'data_extraction',
        'dcf_calculation',
        'pdf_export',
        'ai_query',
    ]
}

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_app_title() -> str:
    """Get the full app title for display"""
    return f"{APP_ICON} {APP_NAME}"

def get_app_header() -> str:
    """Get the formatted header for main page"""
    return f"""
    <div class='main-header'>
        <h1>{APP_ICON} {APP_NAME}</h1>
        <p>{APP_TAGLINE}</p>
    </div>
    """

def get_footer() -> str:
    """Get the footer text"""
    return f"""
    <div class='footer'>
        <p>{APP_NAME} v{APP_VERSION} | {COMPANY_NAME}</p>
        <p>{DISCLAIMERS['main']}</p>
    </div>
    """

def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature is enabled"""
    return FEATURES.get(feature_name, False)

# ==========================================
# EXPORT CONFIGURATION
# ==========================================

if __name__ == "__main__":
    # Print configuration summary
    print("=" * 80)
    print(f"{APP_ICON} {APP_NAME} - Configuration Summary")
    print("=" * 80)
    print(f"\nVersion: {APP_VERSION}")
    print(f"Tagline: {APP_TAGLINE}")
    print(f"\nEnabled Features:")
    for feature, enabled in FEATURES.items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {feature}")
    print(f"\nData Sources:")
    for source_type, source_name in DATA_SOURCES.items():
        print(f"  - {source_type}: {source_name}")
    print("\n" + "=" * 80)


