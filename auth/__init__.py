"""
Authentication Package - MILESTONE-016
======================================
User authentication, authorization, and session management.

Usage:
    from auth import render_auth_page, is_authenticated, get_current_user
    
    # In app:
    if not is_authenticated():
        render_auth_page()
        st.stop()
    
    user = get_current_user()
    
Author: ATLAS Architect
Date: 2025-12-08
"""

from .config import (
    UserTier,
    TierLimits,
    TIER_LIMITS,
    AuthConfig,
    AUTH_CONFIG,
    User,
    MONETIZATION_ENABLED,
    is_monetization_active,
)

from .authenticator import (
    register_user,
    authenticate,
    update_user_usage,
    get_user,
    update_user_tier,
    init_session_state,
    login,
    logout,
    is_authenticated,
    get_current_user,
    require_auth,
    require_tier,
)

from .ui import (
    inject_auth_styles,
    render_login_form,
    render_register_form,
    render_auth_page,
    render_user_sidebar,
    check_usage_limit,
)

__all__ = [
    # Config
    'UserTier',
    'TierLimits',
    'TIER_LIMITS',
    'AuthConfig',
    'AUTH_CONFIG',
    'User',
    'MONETIZATION_ENABLED',
    'is_monetization_active',
    # Authenticator
    'register_user',
    'authenticate',
    'update_user_usage',
    'get_user',
    'update_user_tier',
    'init_session_state',
    'login',
    'logout',
    'is_authenticated',
    'get_current_user',
    'require_auth',
    'require_tier',
    # UI
    'inject_auth_styles',
    'render_login_form',
    'render_register_form',
    'render_auth_page',
    'render_user_sidebar',
    'check_usage_limit',
]

