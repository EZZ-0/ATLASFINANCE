"""
ATLAS Theme Configuration System
=================================
Comprehensive theming for White-Label / B2B customization.

MILESTONE-006: White-Label/Custom Branding
Author: EXECUTOR
Created: 2025-12-08
"""

from typing import Dict, Optional


# =============================================================================
# THEME DEFINITIONS
# =============================================================================

THEMES: Dict[str, Dict] = {
    
    # -------------------------------------------------------------------------
    # ATLAS DARK (Default) - Current production theme
    # -------------------------------------------------------------------------
    'atlas_dark': {
        'name': 'ATLAS Dark',
        'mode': 'dark',
        'description': 'Professional dark theme - Default',
        
        # Core colors
        'primary': '#3b82f6',
        'primary_light': '#60a5fa',
        'primary_dark': '#2563eb',
        'secondary': '#10b981',
        'secondary_light': '#34d399',
        'accent': '#f59e0b',
        'highlight': '#e94560',
        
        # Background colors
        'background': '#0f1419',
        'background_secondary': '#1a1f26',
        'card_bg': '#1e2530',
        'card_bg_alpha': 'rgba(30, 37, 48, 0.9)',
        'hover_bg': '#252d3a',
        
        # Text colors
        'text': '#f0f4f8',
        'text_secondary': '#94a3b8',
        'text_muted': '#64748b',
        
        # Border colors
        'border': 'rgba(148, 163, 184, 0.1)',
        'border_accent': 'rgba(59, 130, 246, 0.3)',
        
        # Status colors
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#3b82f6',
        
        # Gradient
        'gradient': 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        
        # Font
        'font_family': "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    },
    
    # -------------------------------------------------------------------------
    # ATLAS LIGHT - Professional light mode
    # -------------------------------------------------------------------------
    'atlas_light': {
        'name': 'ATLAS Light',
        'mode': 'light',
        'description': 'Clean light theme for daytime use',
        
        # Core colors
        'primary': '#2563eb',
        'primary_light': '#3b82f6',
        'primary_dark': '#1d4ed8',
        'secondary': '#059669',
        'secondary_light': '#10b981',
        'accent': '#d97706',
        'highlight': '#dc2626',
        
        # Background colors
        'background': '#f8fafc',
        'background_secondary': '#f1f5f9',
        'card_bg': '#ffffff',
        'card_bg_alpha': 'rgba(255, 255, 255, 0.95)',
        'hover_bg': '#e2e8f0',
        
        # Text colors
        'text': '#1e293b',
        'text_secondary': '#475569',
        'text_muted': '#94a3b8',
        
        # Border colors
        'border': 'rgba(0, 0, 0, 0.08)',
        'border_accent': 'rgba(37, 99, 235, 0.2)',
        
        # Status colors
        'success': '#059669',
        'warning': '#d97706',
        'danger': '#dc2626',
        'info': '#2563eb',
        
        # Gradient
        'gradient': 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
        
        # Font
        'font_family': "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    },
    
    # -------------------------------------------------------------------------
    # CORPORATE BLUE - B2B friendly professional theme
    # -------------------------------------------------------------------------
    'corporate_blue': {
        'name': 'Corporate',
        'mode': 'dark',
        'description': 'B2B-friendly corporate theme',
        
        # Core colors - More conservative, corporate blues
        'primary': '#1e40af',
        'primary_light': '#3b82f6',
        'primary_dark': '#1e3a8a',
        'secondary': '#0891b2',
        'secondary_light': '#22d3ee',
        'accent': '#0284c7',
        'highlight': '#f97316',
        
        # Background colors - Deep navy
        'background': '#0c1222',
        'background_secondary': '#111827',
        'card_bg': '#1e293b',
        'card_bg_alpha': 'rgba(30, 41, 59, 0.95)',
        'hover_bg': '#334155',
        
        # Text colors
        'text': '#f1f5f9',
        'text_secondary': '#cbd5e1',
        'text_muted': '#64748b',
        
        # Border colors
        'border': 'rgba(100, 116, 139, 0.2)',
        'border_accent': 'rgba(30, 64, 175, 0.4)',
        
        # Status colors
        'success': '#22c55e',
        'warning': '#eab308',
        'danger': '#ef4444',
        'info': '#0ea5e9',
        
        # Gradient
        'gradient': 'linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%)',
        
        # Font - More conservative
        'font_family': "'Arial', 'Helvetica Neue', sans-serif",
    },
    
    # -------------------------------------------------------------------------
    # EMERALD GOLD - Alternative dark theme
    # -------------------------------------------------------------------------
    'emerald_gold': {
        'name': 'Emerald & Gold',
        'mode': 'dark',
        'description': 'Elegant dark theme with green and gold accents',
        
        # Core colors
        'primary': '#10b981',
        'primary_light': '#34d399',
        'primary_dark': '#047857',
        'secondary': '#f59e0b',
        'secondary_light': '#fbbf24',
        'accent': '#06b6d4',
        'highlight': '#f59e0b',
        
        # Background colors
        'background': '#0a1f1a',
        'background_secondary': '#0d2818',
        'card_bg': '#0f3528',
        'card_bg_alpha': 'rgba(15, 53, 40, 0.9)',
        'hover_bg': '#134e3a',
        
        # Text colors
        'text': '#ecfdf5',
        'text_secondary': '#a7f3d0',
        'text_muted': '#6ee7b7',
        
        # Border colors
        'border': 'rgba(16, 185, 129, 0.15)',
        'border_accent': 'rgba(16, 185, 129, 0.4)',
        
        # Status colors
        'success': '#10b981',
        'warning': '#f59e0b',
        'danger': '#ef4444',
        'info': '#06b6d4',
        
        # Gradient
        'gradient': 'linear-gradient(135deg, #10b981 0%, #047857 100%)',
        
        # Font
        'font_family': "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    },
    
    # -------------------------------------------------------------------------
    # PURPLE ROSE - Elegant alternative
    # -------------------------------------------------------------------------
    'purple_rose': {
        'name': 'Purple & Rose',
        'mode': 'dark',
        'description': 'Elegant purple theme with rose accents',
        
        # Core colors
        'primary': '#8b5cf6',
        'primary_light': '#a78bfa',
        'primary_dark': '#6d28d9',
        'secondary': '#f43f5e',
        'secondary_light': '#fb7185',
        'accent': '#ec4899',
        'highlight': '#f43f5e',
        
        # Background colors
        'background': '#1a0a2e',
        'background_secondary': '#2e1065',
        'card_bg': '#3b0764',
        'card_bg_alpha': 'rgba(59, 7, 100, 0.9)',
        'hover_bg': '#4c0a77',
        
        # Text colors
        'text': '#faf5ff',
        'text_secondary': '#e9d5ff',
        'text_muted': '#c4b5fd',
        
        # Border colors
        'border': 'rgba(139, 92, 246, 0.15)',
        'border_accent': 'rgba(139, 92, 246, 0.4)',
        
        # Status colors
        'success': '#22c55e',
        'warning': '#fbbf24',
        'danger': '#f43f5e',
        'info': '#a78bfa',
        
        # Gradient
        'gradient': 'linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)',
        
        # Font
        'font_family': "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_theme(theme_name: str = 'atlas_dark') -> Dict:
    """
    Get theme configuration by name.
    
    Args:
        theme_name: Theme identifier (default: 'atlas_dark')
        
    Returns:
        Theme dictionary with all color/style settings
    """
    return THEMES.get(theme_name, THEMES['atlas_dark'])


def get_theme_names() -> Dict[str, str]:
    """
    Get mapping of theme IDs to display names.
    
    Returns:
        Dict mapping theme_id -> display_name
    """
    return {key: theme['name'] for key, theme in THEMES.items()}


def get_themes_by_mode(mode: str = 'dark') -> Dict[str, Dict]:
    """
    Get themes filtered by mode (light/dark).
    
    Args:
        mode: 'light' or 'dark'
        
    Returns:
        Dict of themes matching the mode
    """
    return {k: v for k, v in THEMES.items() if v.get('mode') == mode}


def get_default_theme() -> str:
    """Get default theme ID."""
    return 'atlas_dark'


# =============================================================================
# WHITE-LABEL CONFIGURATION
# =============================================================================

class WhiteLabelConfig:
    """
    Configuration for white-label customization.
    Future B2B clients can set their own branding here.
    """
    
    def __init__(
        self,
        company_name: str = "ATLAS",
        logo_url: Optional[str] = None,
        theme_name: str = 'atlas_dark',
        custom_colors: Optional[Dict] = None,
        footer_text: Optional[str] = None,
    ):
        self.company_name = company_name
        self.logo_url = logo_url
        self.theme_name = theme_name
        self.custom_colors = custom_colors or {}
        self.footer_text = footer_text
    
    def get_theme(self) -> Dict:
        """Get theme with any custom color overrides."""
        base_theme = get_theme(self.theme_name).copy()
        base_theme.update(self.custom_colors)
        return base_theme


# Default white-label config
DEFAULT_WHITELABEL = WhiteLabelConfig()

