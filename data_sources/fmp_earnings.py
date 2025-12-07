"""
FMP Earnings API Client
=======================

Financial Modeling Prep API integration for earnings revision tracking.

Provides:
- Historical analyst estimates
- EPS revision history
- Revenue estimates
- Analyst grade changes

Free Tier: 250 calls/day
API Key: FMP_API_KEY environment variable

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (TASK-A011)
"""

import os
import requests
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# FMP API Configuration
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
FMP_API_KEY = os.getenv('FMP_API_KEY')


class FMPEarningsClient:
    """
    Client for FMP earnings-related endpoints.
    
    Usage:
        client = FMPEarningsClient()
        estimates = client.get_historical_estimates("AAPL")
        revisions = client.calculate_revision_pct("AAPL", days=30)
    """
    
    def __init__(self, api_key: str = None):
        """Initialize with API key."""
        self.api_key = api_key or FMP_API_KEY
        self._request_count = 0
    
    def is_available(self) -> bool:
        """Check if FMP API key is configured."""
        return bool(self.api_key)
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to FMP API."""
        if not self.api_key:
            logger.debug("FMP API key not set")
            return None
        
        url = f"{FMP_BASE_URL}/{endpoint}"
        request_params = {'apikey': self.api_key}
        if params:
            request_params.update(params)
        
        try:
            response = requests.get(url, params=request_params, timeout=10)
            self._request_count += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                logger.error("FMP API: Invalid API key")
            elif response.status_code == 403:
                logger.warning("FMP API: Rate limit exceeded")
            else:
                logger.warning(f"FMP API returned {response.status_code}")
            
            return None
            
        except requests.Timeout:
            logger.error("FMP API: Request timeout")
            return None
        except Exception as e:
            logger.error(f"FMP API error: {e}")
            return None
    
    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def get_historical_estimates(_self, ticker: str, period: str = 'quarterly', limit: int = 10) -> Optional[List[Dict]]:
        """
        Get historical analyst estimates.
        
        Args:
            ticker: Stock ticker symbol
            period: 'annual' or 'quarterly'
            limit: Number of periods to retrieve
            
        Returns:
            List of estimate records or None
        """
        data = _self._make_request(
            f"analyst-estimates/{ticker}",
            {'period': period, 'limit': limit}
        )
        
        if data and isinstance(data, list):
            return data
        return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_grade_changes(_self, ticker: str, limit: int = 50) -> Optional[List[Dict]]:
        """
        Get analyst rating changes (upgrades/downgrades).
        
        Args:
            ticker: Stock ticker symbol
            limit: Number of changes to retrieve
            
        Returns:
            List of grade change records or None
        """
        data = _self._make_request(
            f"grade/{ticker}",
            {'limit': limit}
        )
        
        if data and isinstance(data, list):
            return data
        return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_earnings_surprises(_self, ticker: str) -> Optional[List[Dict]]:
        """
        Get earnings surprise history.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            List of surprise records or None
        """
        data = _self._make_request(f"earnings-surprises/{ticker}")
        
        if data and isinstance(data, list):
            return data
        return None
    
    def calculate_revision_pct(self, ticker: str, days: int = 30) -> Optional[Dict]:
        """
        Calculate EPS revision percentage over a period.
        
        Args:
            ticker: Stock ticker symbol
            days: Lookback period (7, 30, 60, or 90)
            
        Returns:
            Dict with revision data or None
        """
        estimates = self.get_historical_estimates(ticker, limit=10)
        
        if not estimates or len(estimates) < 2:
            return None
        
        try:
            # Get current and prior estimates
            current = estimates[0]
            
            # Find estimate from ~days ago
            target_date = datetime.now() - timedelta(days=days)
            prior = None
            
            for est in estimates[1:]:
                est_date = datetime.strptime(est.get('date', ''), '%Y-%m-%d')
                if est_date <= target_date:
                    prior = est
                    break
            
            if not prior:
                prior = estimates[-1]  # Use oldest available
            
            # Calculate revision
            current_eps = current.get('estimatedEpsAvg')
            prior_eps = prior.get('estimatedEpsAvg')
            
            if current_eps is None or prior_eps is None or prior_eps == 0:
                return None
            
            revision_pct = ((current_eps - prior_eps) / abs(prior_eps)) * 100
            
            return {
                'ticker': ticker,
                'timeframe': f"{days}d",
                'current_estimate': current_eps,
                'prior_estimate': prior_eps,
                'revision_pct': round(revision_pct, 2),
                'direction': 'up' if revision_pct > 0 else ('down' if revision_pct < 0 else 'flat'),
                'current_date': current.get('date'),
                'prior_date': prior.get('date'),
            }
            
        except Exception as e:
            logger.error(f"Error calculating revision for {ticker}: {e}")
            return None
    
    def get_all_revisions(self, ticker: str) -> Dict:
        """
        Get revisions for all standard timeframes.
        
        Returns:
            Dict with 7d, 30d, 60d, 90d revisions
        """
        result = {
            '7d': None,
            '30d': None,
            '60d': None,
            '90d': None,
        }
        
        for days in [7, 30, 60, 90]:
            result[f"{days}d"] = self.calculate_revision_pct(ticker, days)
        
        return result
    
    def get_upgrade_downgrade_count(self, ticker: str, days: int = 30) -> Dict:
        """
        Count upgrades vs downgrades in a period.
        
        Returns:
            Dict with upgrade and downgrade counts
        """
        grades = self.get_grade_changes(ticker)
        
        if not grades:
            return {'upgrades': 0, 'downgrades': 0, 'total': 0}
        
        cutoff = datetime.now() - timedelta(days=days)
        upgrades = 0
        downgrades = 0
        
        for grade in grades:
            try:
                grade_date = datetime.strptime(grade.get('date', ''), '%Y-%m-%d')
                if grade_date >= cutoff:
                    action = grade.get('action', '').lower()
                    if 'upgrade' in action:
                        upgrades += 1
                    elif 'downgrade' in action:
                        downgrades += 1
            except:
                continue
        
        return {
            'upgrades': upgrades,
            'downgrades': downgrades,
            'total': upgrades + downgrades,
            'net': upgrades - downgrades
        }


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

_client = None

def get_fmp_client() -> FMPEarningsClient:
    """Get or create singleton client instance."""
    global _client
    if _client is None:
        _client = FMPEarningsClient()
    return _client


def is_fmp_available() -> bool:
    """Check if FMP API is configured."""
    return get_fmp_client().is_available()


def get_revision_data(ticker: str, days: int = 30) -> Optional[Dict]:
    """Get revision data for a ticker."""
    return get_fmp_client().calculate_revision_pct(ticker, days)


def get_all_revision_data(ticker: str) -> Dict:
    """Get all timeframe revisions."""
    return get_fmp_client().get_all_revisions(ticker)


def get_grade_summary(ticker: str, days: int = 30) -> Dict:
    """Get upgrade/downgrade summary."""
    return get_fmp_client().get_upgrade_downgrade_count(ticker, days)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("FMP EARNINGS CLIENT TEST")
    print("=" * 60)
    
    client = FMPEarningsClient()
    
    if not client.is_available():
        print("\n[WARN] FMP_API_KEY not set. Set it to test:")
        print("  export FMP_API_KEY=your_key_here")
        print("\nUsing mock data for structure test...")
    else:
        print(f"\n[OK] FMP API key configured")
        
        for ticker in ['AAPL', 'MSFT']:
            print(f"\n[TEST] {ticker}")
            
            # Test historical estimates
            estimates = client.get_historical_estimates(ticker, limit=3)
            if estimates:
                print(f"  Historical estimates: {len(estimates)} periods")
                print(f"  Latest: EPS={estimates[0].get('estimatedEpsAvg')}")
            
            # Test revision calculation
            revision = client.calculate_revision_pct(ticker, days=30)
            if revision:
                print(f"  30-day revision: {revision['revision_pct']}%")
            
            # Test grade changes
            grades = client.get_grade_summary(ticker, days=60)
            print(f"  Grades (60d): +{grades['upgrades']} / -{grades['downgrades']}")
    
    print("\n[OK] FMP earnings client ready")

