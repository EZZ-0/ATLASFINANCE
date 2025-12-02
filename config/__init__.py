"""
Config package for Saudi Earnings Engine
Contains app configuration and theme presets
"""

from .app_config import (
    APP_NAME, APP_NAME_SHORT, APP_TAGLINE, APP_VERSION,
    FEATURES, is_feature_enabled,
    get_app_title, get_app_header, get_footer
)

__all__ = [
    'APP_NAME', 'APP_NAME_SHORT', 'APP_TAGLINE', 'APP_VERSION',
    'FEATURES', 'is_feature_enabled',
    'get_app_title', 'get_app_header', 'get_footer'
]


