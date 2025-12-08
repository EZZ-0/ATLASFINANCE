"""
SEC EDGAR API Client
====================

Official SEC data access for:
- Form 4 (Insider transactions)
- Company info (CIK mapping)
- Filing metadata

Rate Limit: 10 requests/second
Required: User-Agent header with contact info

Author: ATLAS Financial Intelligence
Created: 2025-12-08 (TASK-A014)
"""

import requests
import pandas as pd
import streamlit as st
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import time

logger = logging.getLogger(__name__)


# SEC API base URLs
SEC_SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SEC_COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

# Required User-Agent header
SEC_USER_AGENT = "ATLAS Financial Intelligence support@atlas-finance.com"

# Rate limiting
RATE_LIMIT_DELAY = 0.1  # 100ms between requests (10 req/sec)


class SECEdgarClient:
    """
    Client for SEC EDGAR API.
    
    Usage:
        client = SECEdgarClient()
        cik = client.get_cik("AAPL")
        filings = client.get_form4_filings(cik)
    """
    
    def __init__(self):
        """Initialize the SEC EDGAR client."""
        self._ticker_cik_cache = None
        self._last_request_time = 0
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()
    
    def _make_request(self, url: str) -> Optional[Dict]:
        """Make a rate-limited request to SEC API."""
        self._rate_limit()
        
        headers = {
            'User-Agent': SEC_USER_AGENT,
            'Accept-Encoding': 'gzip, deflate'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("SEC rate limit hit, waiting...")
                time.sleep(1)
                return self._make_request(url)
            else:
                logger.warning(f"SEC API returned {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"SEC API error: {e}")
            return None
    
    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def get_ticker_cik_map(_self) -> Dict[str, str]:
        """
        Get mapping of tickers to CIK numbers.
        
        Returns:
            Dict mapping ticker -> CIK (zero-padded to 10 digits)
        """
        if _self._ticker_cik_cache:
            return _self._ticker_cik_cache
        
        data = _self._make_request(SEC_COMPANY_TICKERS_URL)
        
        if not data:
            logger.error("Failed to fetch ticker-CIK mapping")
            return {}
        
        # Parse response: {index: {cik_str, ticker, title}}
        mapping = {}
        for entry in data.values():
            ticker = entry.get('ticker', '').upper()
            cik = str(entry.get('cik_str', ''))
            if ticker and cik:
                mapping[ticker] = cik.zfill(10)
        
        _self._ticker_cik_cache = mapping
        return mapping
    
    def get_cik(self, ticker: str) -> Optional[str]:
        """
        Get CIK for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            CIK (10-digit, zero-padded) or None
        """
        mapping = self.get_ticker_cik_map()
        return mapping.get(ticker.upper())
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_company_info(_self, ticker: str) -> Optional[Dict]:
        """
        Get company info from SEC.
        
        Returns:
            Dict with company name, SIC, entity type, etc.
        """
        cik = _self.get_cik(ticker)
        if not cik:
            logger.warning(f"No CIK found for {ticker}")
            return None
        
        url = SEC_SUBMISSIONS_URL.format(cik=cik)
        data = _self._make_request(url)
        
        if not data:
            return None
        
        return {
            'cik': data.get('cik'),
            'name': data.get('name'),
            'sic': data.get('sic'),
            'sic_description': data.get('sicDescription'),
            'entity_type': data.get('entityType'),
            'tickers': data.get('tickers', []),
            'exchanges': data.get('exchanges', []),
            'state': data.get('stateOfIncorporation'),
            'fiscal_year_end': data.get('fiscalYearEnd')
        }
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_recent_filings(_self, ticker: str, form_type: str = None, limit: int = 100) -> List[Dict]:
        """
        Get recent filings for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            form_type: Filter by form type (e.g., "4", "10-K", "8-K")
            limit: Maximum number of filings to return
            
        Returns:
            List of filing metadata dicts
        """
        cik = _self.get_cik(ticker)
        if not cik:
            return []
        
        url = SEC_SUBMISSIONS_URL.format(cik=cik)
        data = _self._make_request(url)
        
        if not data or 'filings' not in data:
            return []
        
        recent = data['filings'].get('recent', {})
        
        filings = []
        for i in range(min(limit, len(recent.get('accessionNumber', [])))):
            form = recent['form'][i]
            
            # Filter by form type if specified
            if form_type and form != form_type:
                continue
            
            filings.append({
                'accession_number': recent['accessionNumber'][i],
                'filing_date': recent['filingDate'][i],
                'form': form,
                'primary_document': recent.get('primaryDocument', [None])[i],
                'description': recent.get('primaryDocDescription', [None])[i],
                'file_number': recent.get('fileNumber', [None])[i],
            })
        
        return filings
    
    def get_form4_filings(self, ticker: str, days: int = 90) -> List[Dict]:
        """
        Get Form 4 (insider transaction) filings.
        
        Args:
            ticker: Stock ticker symbol
            days: Lookback period in days
            
        Returns:
            List of Form 4 filing metadata
        """
        filings = self.get_recent_filings(ticker, form_type='4', limit=200)
        
        if not filings:
            return []
        
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            f for f in filings
            if datetime.strptime(f['filing_date'], '%Y-%m-%d') >= cutoff
        ]


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

_client = None

def get_client() -> SECEdgarClient:
    """Get or create singleton client instance."""
    global _client
    if _client is None:
        _client = SECEdgarClient()
    return _client


def get_cik(ticker: str) -> Optional[str]:
    """Get CIK for a ticker."""
    return get_client().get_cik(ticker)


def get_company_info(ticker: str) -> Optional[Dict]:
    """Get SEC company info for a ticker."""
    return get_client().get_company_info(ticker)


def get_form4_count(ticker: str, days: int = 90) -> int:
    """Get count of Form 4 filings in the period."""
    filings = get_client().get_form4_filings(ticker, days)
    return len(filings)


def get_insider_filing_dates(ticker: str, days: int = 90) -> List[str]:
    """Get list of Form 4 filing dates."""
    filings = get_client().get_form4_filings(ticker, days)
    return [f['filing_date'] for f in filings]


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("SEC EDGAR API TEST")
    print("=" * 60)
    
    client = SECEdgarClient()
    
    for ticker in ['AAPL', 'MSFT', 'NVDA']:
        print(f"\n[TEST] {ticker}")
        
        cik = client.get_cik(ticker)
        print(f"  CIK: {cik}")
        
        if cik:
            info = client.get_company_info(ticker)
            print(f"  Name: {info.get('name') if info else 'N/A'}")
            
            form4s = client.get_form4_filings(ticker, days=30)
            print(f"  Form 4s (30 days): {len(form4s)}")
    
    print("\n[OK] SEC EDGAR module ready")

