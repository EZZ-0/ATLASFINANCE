# FMP Earnings API Research

**Task:** E012  
**Completed By:** Executor  
**Date:** 2025-12-08  
**Status:** COMPLETE ✅

---

## 1. Summary

| Feature | Available | Quality |
|---------|-----------|---------|
| Current EPS Estimates | ✅ Yes | Excellent |
| Revenue Estimates | ✅ Yes | Excellent |
| Historical Estimates | ✅ Yes | Excellent |
| Revision Dates | ✅ Yes | Excellent |
| Analyst Grades | ✅ Yes | Excellent |
| Price Targets | ✅ Yes | Good |

**Bottom Line:** FMP provides COMPLETE revision tracking. Best option for revision history.

---

## 2. FMP API Overview

**Base URL:** `https://financialmodelingprep.com/api/v3/`

**Authentication:** API key required (`?apikey=YOUR_KEY`)

**Free Tier:** 250 calls/day

**Documentation:** https://site.financialmodelingprep.com/developer/docs

---

## 3. Key Endpoints for Earnings Revisions

### 3.1 Analyst Estimates

**Endpoint:** `/analyst-estimates/{symbol}`

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `symbol` | string | Ticker symbol |
| `period` | string | "annual" or "quarterly" |
| `limit` | int | Number of records |

**Response Fields:**
```json
{
  "symbol": "AAPL",
  "date": "2024-12-31",
  "estimatedRevenueLow": 115000000000,
  "estimatedRevenueHigh": 125000000000,
  "estimatedRevenueAvg": 120000000000,
  "estimatedEbitdaLow": 40000000000,
  "estimatedEbitdaHigh": 45000000000,
  "estimatedEbitdaAvg": 42500000000,
  "estimatedEpsLow": 1.40,
  "estimatedEpsHigh": 1.70,
  "estimatedEpsAvg": 1.55,
  "numberAnalystEstimatedRevenue": 35,
  "numberAnalystsEstimatedEps": 42
}
```

**Use Cases:**
- Track EPS estimate changes over time
- Compare current vs. historical estimates
- Calculate revision momentum

### 3.2 Analyst Grades (Rating Changes)

**Endpoint:** `/grade/{symbol}`

**Response Fields:**
```json
{
  "symbol": "AAPL",
  "date": "2024-11-15",
  "gradingCompany": "Morgan Stanley",
  "previousGrade": "Equal-Weight",
  "newGrade": "Overweight",
  "action": "upgrade"
}
```

**Use Cases:**
- Track upgrades/downgrades
- Calculate net rating change
- Identify sentiment shifts

### 3.3 Earnings Calendar

**Endpoint:** `/earning_calendar`

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `from` | date | Start date (YYYY-MM-DD) |
| `to` | date | End date (YYYY-MM-DD) |

**Response Fields:**
- `date`: Earnings date
- `symbol`: Ticker
- `eps`: EPS estimate
- `epsEstimated`: Consensus
- `revenue`: Revenue estimate
- `revenueEstimated`: Consensus revenue

### 3.4 Earnings Surprises

**Endpoint:** `/earnings-surprises/{symbol}`

**Response Fields:**
```json
{
  "date": "2024-10-31",
  "symbol": "AAPL",
  "actualEarningResult": 1.64,
  "estimatedEarning": 1.60,
  "surprisePercent": 2.5
}
```

---

## 4. Rate Limits & Pricing

| Plan | Calls/Day | Calls/Min | Price |
|------|-----------|-----------|-------|
| Free | 250 | 5 | $0 |
| Basic | Unlimited | 300 | $19/mo |
| Professional | Unlimited | 750 | $49/mo |
| Enterprise | Unlimited | 1200 | Custom |

**For ATLAS:**
- Free tier (250/day) sufficient for development
- Basic tier recommended for production
- Each ticker analysis uses ~3-5 calls

---

## 5. Sample API Calls

### Get Historical EPS Estimates (for revision tracking)

```python
import requests
import os

FMP_API_KEY = os.getenv('FMP_API_KEY')

def get_historical_estimates(ticker: str, limit: int = 10):
    """Get historical analyst estimates for revision tracking."""
    url = f"https://financialmodelingprep.com/api/v3/analyst-estimates/{ticker}"
    params = {
        'apikey': FMP_API_KEY,
        'period': 'quarterly',
        'limit': limit
    }
    response = requests.get(url, params=params)
    return response.json()

# Returns list of estimates over time
# Can compare estimates to calculate revision %
```

### Get Analyst Grade Changes

```python
def get_grade_changes(ticker: str):
    """Get recent analyst rating changes."""
    url = f"https://financialmodelingprep.com/api/v3/grade/{ticker}"
    params = {'apikey': FMP_API_KEY}
    response = requests.get(url, params=params)
    return response.json()

# Returns chronological list of rating changes
# Can count upgrades vs downgrades
```

### Calculate Revision Momentum

```python
def calculate_eps_revision(ticker: str, days: int = 30):
    """Calculate EPS revision over period."""
    estimates = get_historical_estimates(ticker, limit=10)
    
    if len(estimates) < 2:
        return {'revision_pct': None, 'status': 'insufficient_data'}
    
    current = estimates[0]['estimatedEpsAvg']
    prior = estimates[1]['estimatedEpsAvg']  # Previous period
    
    revision_pct = ((current - prior) / abs(prior)) * 100 if prior else 0
    
    return {
        'current_estimate': current,
        'prior_estimate': prior,
        'revision_pct': revision_pct,
        'direction': 'up' if revision_pct > 0 else ('down' if revision_pct < 0 else 'flat')
    }
```

---

## 6. FMP vs yfinance Comparison

| Feature | yfinance | FMP |
|---------|----------|-----|
| Current EPS | ✅ | ✅ |
| Revenue Estimates | ❌ | ✅ |
| Historical Estimates | ❌ | ✅ |
| Revision % Calculation | ❌ | ✅ |
| Analyst Grades | ✅ | ✅ |
| Individual Analyst Data | ❌ | ✅ |
| Free Unlimited | ✅ | ❌ (250/day) |
| API Key Required | ❌ | ✅ |

---

## 7. Integration with ATLAS

### Current FMP Support

ATLAS already has FMP integration in `data_sources/`:
- Check for `FMP_API_KEY` environment variable
- Used in `earnings_revisions.py` as backup source

### Recommended Implementation

```python
class FMPClient:
    """FMP API client for earnings data."""
    
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('FMP_API_KEY')
        
    def get_analyst_estimates(self, ticker: str, period: str = 'quarterly', limit: int = 10):
        """Get historical analyst estimates."""
        if not self.api_key:
            return None
        url = f"{self.BASE_URL}/analyst-estimates/{ticker}"
        params = {'apikey': self.api_key, 'period': period, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        return response.json() if response.ok else None
    
    def get_grade_changes(self, ticker: str, limit: int = 50):
        """Get analyst rating changes."""
        if not self.api_key:
            return None
        url = f"{self.BASE_URL}/grade/{ticker}"
        params = {'apikey': self.api_key, 'limit': limit}
        response = requests.get(url, params=params, timeout=10)
        return response.json() if response.ok else None
```

---

## 8. Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 | Invalid API key | Check FMP_API_KEY env var |
| 403 | Rate limit exceeded | Wait or upgrade plan |
| 404 | Unknown ticker | Validate ticker first |
| 429 | Too many requests | Implement exponential backoff |
| 5xx | Server error | Retry with backoff |

**Fallback Strategy:**
- If FMP fails → Use yfinance current data only
- Log warning about limited functionality
- Don't block user flow

---

## 9. API Key Setup

### Getting Free Key

1. Go to: https://financialmodelingprep.com/developer
2. Create free account
3. Navigate to Dashboard > API Key
4. Copy key

### Setting in ATLAS

```bash
# Windows PowerShell
$env:FMP_API_KEY = "your_key_here"

# Or add to .env file
FMP_API_KEY=your_key_here
```

---

## 10. Conclusion

**FMP is the BEST source for revision tracking because:**

✅ Full historical estimates (not just current)
✅ Revenue estimates (not just EPS)
✅ Individual analyst data available
✅ Grade changes with dates
✅ Well-documented API
✅ Generous free tier (250/day)

**Limitations:**
- Requires API key (free registration)
- Rate limited on free tier
- Some fields only on paid plans

**Recommendation:** Use FMP as PRIMARY source for revision tracking.

