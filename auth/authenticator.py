"""
AUTHENTICATOR - MILESTONE-016
=============================
Handles user login, registration, and session management.

Uses YAML file for MVP user storage.
Designed for easy migration to Supabase/Firebase.

Author: ATLAS Architect
Date: 2025-12-08
"""

import streamlit as st
import yaml
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from pathlib import Path

from .config import AUTH_CONFIG, User, UserTier, TIER_LIMITS


# ============================================================================
# USER STORAGE (MVP - YAML file, migrate to DB later)
# ============================================================================

USERS_FILE = Path(__file__).parent / "users.yaml"


def _hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """Hash password with salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000
    ).hex()
    return hashed, salt


def _verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify password against hash."""
    check_hash, _ = _hash_password(password, salt)
    return check_hash == hashed


def _load_users() -> Dict:
    """Load users from YAML file."""
    if not USERS_FILE.exists():
        return {"users": {}}
    
    with open(USERS_FILE, 'r') as f:
        return yaml.safe_load(f) or {"users": {}}


def _save_users(data: Dict) -> None:
    """Save users to YAML file."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def register_user(username: str, email: str, name: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user.
    
    Returns:
        (success, message)
    """
    # Validate password
    valid, msg = AUTH_CONFIG.validate_password(password)
    if not valid:
        return False, msg
    
    # Load existing users
    data = _load_users()
    
    # Check if username exists
    if username.lower() in [u.lower() for u in data["users"].keys()]:
        return False, "Username already exists"
    
    # Check if email exists
    for user_data in data["users"].values():
        if user_data.get("email", "").lower() == email.lower():
            return False, "Email already registered"
    
    # Hash password
    hashed, salt = _hash_password(password)
    
    # Create user
    data["users"][username] = {
        "email": email,
        "name": name,
        "password_hash": hashed,
        "password_salt": salt,
        "tier": UserTier.FREE.value,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "last_login": "",
        "analyses_today": 0,
        "total_analyses": 0,
        "theme": "atlas_dark",
        "dashboard_layout": [],
    }
    
    # Save
    _save_users(data)
    
    return True, "Registration successful! Please login."


def authenticate(username: str, password: str) -> Tuple[bool, Optional[User], str]:
    """
    Authenticate a user.
    
    Returns:
        (success, user_object, message)
    """
    data = _load_users()
    
    # Find user (case-insensitive)
    user_key = None
    for key in data["users"].keys():
        if key.lower() == username.lower():
            user_key = key
            break
    
    if user_key is None:
        return False, None, "Invalid username or password"
    
    user_data = data["users"][user_key]
    
    # Check if active
    if not user_data.get("is_active", True):
        return False, None, "Account is deactivated"
    
    # Verify password
    if not _verify_password(
        password,
        user_data.get("password_hash", ""),
        user_data.get("password_salt", "")
    ):
        return False, None, "Invalid username or password"
    
    # Update last login
    user_data["last_login"] = datetime.now().isoformat()
    
    # Reset daily counter if new day
    last_login = user_data.get("last_login_date", "")
    today = datetime.now().strftime("%Y-%m-%d")
    if last_login != today:
        user_data["analyses_today"] = 0
        user_data["last_login_date"] = today
    
    data["users"][user_key] = user_data
    _save_users(data)
    
    # Create User object
    user = User(
        username=user_key,
        email=user_data.get("email", ""),
        name=user_data.get("name", ""),
        tier=UserTier(user_data.get("tier", "free")),
        is_active=user_data.get("is_active", True),
        created_at=user_data.get("created_at", ""),
        last_login=user_data.get("last_login", ""),
        analyses_today=user_data.get("analyses_today", 0),
        total_analyses=user_data.get("total_analyses", 0),
        theme=user_data.get("theme", "atlas_dark"),
        dashboard_layout=user_data.get("dashboard_layout", []),
    )
    
    return True, user, "Login successful"


def update_user_usage(username: str) -> None:
    """Increment user's analysis count."""
    data = _load_users()
    
    if username in data["users"]:
        data["users"][username]["analyses_today"] = \
            data["users"][username].get("analyses_today", 0) + 1
        data["users"][username]["total_analyses"] = \
            data["users"][username].get("total_analyses", 0) + 1
        _save_users(data)


def get_user(username: str) -> Optional[User]:
    """Get user by username."""
    data = _load_users()
    
    if username not in data["users"]:
        return None
    
    user_data = data["users"][username]
    return User.from_dict({"username": username, **user_data})


def update_user_tier(username: str, new_tier: UserTier) -> bool:
    """Update user's subscription tier."""
    data = _load_users()
    
    if username not in data["users"]:
        return False
    
    data["users"][username]["tier"] = new_tier.value
    _save_users(data)
    return True


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

def init_session_state() -> None:
    """Initialize authentication session state."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None
    if "auth_message" not in st.session_state:
        st.session_state.auth_message = ""


def login(username: str, password: str) -> bool:
    """Login and set session state."""
    success, user, message = authenticate(username, password)
    
    if success:
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.auth_message = message
        return True
    else:
        st.session_state.auth_message = message
        return False


def logout() -> None:
    """Logout and clear session."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.auth_message = "Logged out successfully"


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> Optional[User]:
    """Get current logged-in user."""
    return st.session_state.get("user", None)


def require_auth(func):
    """Decorator to require authentication for a function."""
    def wrapper(*args, **kwargs):
        if not is_authenticated():
            st.warning("Please login to access this feature.")
            return None
        return func(*args, **kwargs)
    return wrapper


def require_tier(min_tier: UserTier):
    """Decorator to require minimum tier for a function."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None:
                st.warning("Please login to access this feature.")
                return None
            
            tier_order = [UserTier.FREE, UserTier.PRO, UserTier.ENTERPRISE]
            if tier_order.index(user.tier) < tier_order.index(min_tier):
                st.warning(f"This feature requires {min_tier.value.upper()} subscription.")
                return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
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
]

