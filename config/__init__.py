"""
Config package for Saudi Earnings Engine
Contains app configuration and theme presets
"""

from .app_config import (
    APP_NAME, APP_NAME_SHORT, APP_TAGLINE, APP_VERSION,
    FEATURES, is_feature_enabled,
    get_app_title, get_app_header, get_footer
)

from .themes import (
    THEMES, get_theme, get_theme_names, get_themes_by_mode,
    get_default_theme, WhiteLabelConfig, DEFAULT_WHITELABEL
)

__all__ = [
    # App config
    'APP_NAME', 'APP_NAME_SHORT', 'APP_TAGLINE', 'APP_VERSION',
    'FEATURES', 'is_feature_enabled',
    'get_app_title', 'get_app_header', 'get_footer',
    # Themes
    'THEMES', 'get_theme', 'get_theme_names', 'get_themes_by_mode',
    'get_default_theme', 'WhiteLabelConfig', 'DEFAULT_WHITELABEL'
]


