"""
AUTHENTICATION CONFIGURATION - MILESTONE-016
=============================================
User authentication for ATLAS Financial Intelligence.

Uses streamlit-authenticator for MVP, designed for easy migration to Supabase.

Author: ATLAS Architect
Date: 2025-12-08
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# MONETIZATION FLAG - Controls whether auth/limits are enforced
# ============================================================================
# Set to True when ready to charge users
# During development: False = everyone gets unlimited free access

MONETIZATION_ENABLED = os.getenv("MONETIZATION_ENABLED", "false").lower() == "true"

# Quick override for testing (set True to test auth flow locally)
FORCE_AUTH_FOR_TESTING = False

def is_monetization_active() -> bool:
    """Check if monetization features should be enforced."""
    return MONETIZATION_ENABLED or FORCE_AUTH_FOR_TESTING

# ============================================================================
# USER TIERS (for M017 - Usage Limits)
# ============================================================================

class UserTier(Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class TierLimits:
    """Usage limits per tier."""
    daily_analyses: int
    saved_watchlist: int
    pdf_exports: int
    api_calls: int
    features: List[str]


TIER_LIMITS = {
    UserTier.FREE: TierLimits(
        daily_analyses=5,
        saved_watchlist=3,
        pdf_exports=2,
        api_calls=0,
        features=["basic_analysis", "flip_cards"]
    ),
    UserTier.PRO: TierLimits(
        daily_analyses=50,
        saved_watchlist=25,
        pdf_exports=20,
        api_calls=100,
        features=["basic_analysis", "flip_cards", "alpha_signals", "dcf", "monte_carlo", "pdf_export"]
    ),
    UserTier.ENTERPRISE: TierLimits(
        daily_analyses=-1,  # Unlimited
        saved_watchlist=-1,
        pdf_exports=-1,
        api_calls=-1,
        features=["all"]
    ),
}


# ============================================================================
# AUTH CONFIGURATION
# ============================================================================

@dataclass
class AuthConfig:
    """Authentication configuration."""
    
    # Cookie settings
    cookie_name: str = "atlas_auth"
    cookie_key: str = field(default_factory=lambda: os.getenv("AUTH_COOKIE_KEY", "atlas_secret_key_change_in_production"))
    cookie_expiry_days: int = 30
    
    # Password requirements
    min_password_length: int = 8
    require_special_char: bool = True
    require_number: bool = True
    
    # Session settings
    session_timeout_minutes: int = 60
    
    # Rate limiting
    max_login_attempts: int = 5
    lockout_minutes: int = 15
    
    # Feature flags
    allow_registration: bool = True
    require_email_verification: bool = False  # Set True for production
    
    def validate_password(self, password: str) -> tuple[bool, str]:
        """Validate password meets requirements."""
        if len(password) < self.min_password_length:
            return False, f"Password must be at least {self.min_password_length} characters"
        
        if self.require_number and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        if self.require_special_char and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"


# Default configuration
AUTH_CONFIG = AuthConfig()


# ============================================================================
# USER DATA STRUCTURE
# ============================================================================

@dataclass
class User:
    """User data model."""
    username: str
    email: str
    name: str
    tier: UserTier = UserTier.FREE
    is_active: bool = True
    created_at: str = ""
    last_login: str = ""
    
    # Usage tracking
    analyses_today: int = 0
    total_analyses: int = 0
    
    # Preferences
    theme: str = "atlas_dark"
    dashboard_layout: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "username": self.username,
            "email": self.email,
            "name": self.name,
            "tier": self.tier.value,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "analyses_today": self.analyses_today,
            "total_analyses": self.total_analyses,
            "theme": self.theme,
            "dashboard_layout": self.dashboard_layout,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "User":
        """Create from dictionary."""
        return cls(
            username=data.get("username", ""),
            email=data.get("email", ""),
            name=data.get("name", ""),
            tier=UserTier(data.get("tier", "free")),
            is_active=data.get("is_active", True),
            created_at=data.get("created_at", ""),
            last_login=data.get("last_login", ""),
            analyses_today=data.get("analyses_today", 0),
            total_analyses=data.get("total_analyses", 0),
            theme=data.get("theme", "atlas_dark"),
            dashboard_layout=data.get("dashboard_layout", []),
        )
    
    def can_analyze(self) -> tuple[bool, str]:
        """Check if user can perform another analysis."""
        limits = TIER_LIMITS[self.tier]
        
        if limits.daily_analyses == -1:
            return True, "Unlimited"
        
        if self.analyses_today >= limits.daily_analyses:
            return False, f"Daily limit reached ({limits.daily_analyses}). Upgrade to Pro for more."
        
        remaining = limits.daily_analyses - self.analyses_today
        return True, f"{remaining} analyses remaining today"
    
    def has_feature(self, feature: str) -> bool:
        """Check if user has access to a feature."""
        limits = TIER_LIMITS[self.tier]
        return "all" in limits.features or feature in limits.features


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'UserTier',
    'TierLimits',
    'TIER_LIMITS',
    'AuthConfig',
    'AUTH_CONFIG',
    'User',
]

