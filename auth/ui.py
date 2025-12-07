"""
AUTHENTICATION UI - MILESTONE-016
=================================
Login, registration, and user profile UI components.

Author: ATLAS Architect
Date: 2025-12-08
"""

import streamlit as st
from typing import Optional, Callable

from .config import User, UserTier, TIER_LIMITS
from .authenticator import (
    init_session_state,
    login,
    logout,
    register_user,
    is_authenticated,
    get_current_user,
)


# ============================================================================
# STYLES
# ============================================================================

AUTH_STYLES = """
<style>
.auth-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: linear-gradient(180deg, rgba(30, 37, 48, 0.95) 0%, rgba(22, 27, 34, 0.95) 100%);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.auth-title {
    text-align: center;
    color: #e6edf3;
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.auth-subtitle {
    text-align: center;
    color: #8b949e;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}
.tier-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}
.tier-free { background: #374151; color: #9ca3af; }
.tier-pro { background: #1e40af; color: #93c5fd; }
.tier-enterprise { background: #7c3aed; color: #c4b5fd; }
.usage-bar {
    height: 8px;
    background: #374151;
    border-radius: 4px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.usage-fill {
    height: 100%;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 4px;
    transition: width 0.3s ease;
}
</style>
"""


def inject_auth_styles():
    """Inject authentication CSS styles."""
    st.markdown(AUTH_STYLES, unsafe_allow_html=True)


# ============================================================================
# LOGIN FORM
# ============================================================================

def render_login_form(on_success: Optional[Callable] = None) -> bool:
    """
    Render login form.
    
    Args:
        on_success: Callback function to run after successful login
    
    Returns:
        True if login successful, False otherwise
    """
    inject_auth_styles()
    
    st.markdown("""
    <div class="auth-title">Welcome Back</div>
    <div class="auth-subtitle">Sign in to your ATLAS account</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            remember = st.checkbox("Remember me")
        with col2:
            st.markdown("<div style='text-align: right; padding-top: 5px;'><a href='#' style='color: #60a5fa; text-decoration: none; font-size: 0.9rem;'>Forgot password?</a></div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return False
            
            if login(username, password):
                st.success("Login successful!")
                if on_success:
                    on_success()
                st.rerun()
                return True
            else:
                st.error(st.session_state.get("auth_message", "Login failed"))
                return False
    
    return False


# ============================================================================
# REGISTRATION FORM
# ============================================================================

def render_register_form(on_success: Optional[Callable] = None) -> bool:
    """
    Render registration form.
    
    Args:
        on_success: Callback function to run after successful registration
    
    Returns:
        True if registration successful, False otherwise
    """
    inject_auth_styles()
    
    st.markdown("""
    <div class="auth-title">Create Account</div>
    <div class="auth-subtitle">Start your free trial with ATLAS</div>
    """, unsafe_allow_html=True)
    
    with st.form("register_form", clear_on_submit=False):
        name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="john@example.com")
        username = st.text_input("Username", placeholder="Choose a username")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input("Password", type="password", placeholder="Min 8 characters")
        with col2:
            confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
        
        terms = st.checkbox("I agree to the Terms of Service and Privacy Policy")
        
        submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        
        if submitted:
            # Validation
            if not all([name, email, username, password, confirm]):
                st.error("Please fill in all fields")
                return False
            
            if password != confirm:
                st.error("Passwords do not match")
                return False
            
            if not terms:
                st.error("Please agree to the Terms of Service")
                return False
            
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email address")
                return False
            
            # Register
            success, message = register_user(username, email, name, password)
            
            if success:
                st.success(message)
                if on_success:
                    on_success()
                return True
            else:
                st.error(message)
                return False
    
    return False


# ============================================================================
# AUTH PAGE (Combined Login/Register)
# ============================================================================

def render_auth_page() -> bool:
    """
    Render combined authentication page with tabs for login/register.
    
    Returns:
        True if user is now authenticated
    """
    init_session_state()
    
    if is_authenticated():
        return True
    
    # Center the form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_register_form()
    
    return is_authenticated()


# ============================================================================
# USER PROFILE SIDEBAR
# ============================================================================

def render_user_sidebar() -> None:
    """Render user profile section in sidebar."""
    user = get_current_user()
    
    if user is None:
        st.sidebar.markdown("---")
        if st.sidebar.button("Sign In", use_container_width=True):
            st.session_state.show_auth = True
        return
    
    st.sidebar.markdown("---")
    
    # User info
    tier_class = f"tier-{user.tier.value}"
    st.sidebar.markdown(f"""
    <div style="padding: 1rem; background: rgba(30, 37, 48, 0.8); border-radius: 12px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <span style="color: #e6edf3; font-weight: 600;">{user.name}</span>
            <span class="tier-badge {tier_class}">{user.tier.value}</span>
        </div>
        <div style="color: #8b949e; font-size: 0.85rem;">{user.email}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Usage stats
    limits = TIER_LIMITS[user.tier]
    if limits.daily_analyses > 0:
        used_pct = min(100, (user.analyses_today / limits.daily_analyses) * 100)
        remaining = limits.daily_analyses - user.analyses_today
        
        st.sidebar.markdown(f"""
        <div style="padding: 0.75rem; background: rgba(30, 37, 48, 0.6); border-radius: 8px; margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; color: #8b949e; font-size: 0.8rem; margin-bottom: 0.25rem;">
                <span>Daily Analyses</span>
                <span>{user.analyses_today}/{limits.daily_analyses}</span>
            </div>
            <div class="usage-bar">
                <div class="usage-fill" style="width: {used_pct}%;"></div>
            </div>
            <div style="color: #6b7280; font-size: 0.75rem; margin-top: 0.25rem;">
                {remaining} remaining today
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Upgrade button for free users
    if user.tier == UserTier.FREE:
        if st.sidebar.button("Upgrade to Pro", use_container_width=True, type="primary"):
            st.session_state.show_upgrade = True
    
    # Logout
    if st.sidebar.button("Sign Out", use_container_width=True):
        logout()
        st.rerun()


# ============================================================================
# USAGE LIMIT CHECK
# ============================================================================

def check_usage_limit() -> bool:
    """
    Check if current user can perform an analysis.
    Shows warning if limit reached.
    
    Returns:
        True if user can analyze, False if limit reached
    """
    user = get_current_user()
    
    if user is None:
        # Not logged in - allow limited access
        return True
    
    can_analyze, message = user.can_analyze()
    
    if not can_analyze:
        st.warning(f"⚠️ {message}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Upgrade to Pro", use_container_width=True, type="primary"):
                st.session_state.show_upgrade = True
        
        return False
    
    return True


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'inject_auth_styles',
    'render_login_form',
    'render_register_form',
    'render_auth_page',
    'render_user_sidebar',
    'check_usage_limit',
]

