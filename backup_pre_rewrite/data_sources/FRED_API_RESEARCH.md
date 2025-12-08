# FRED API Research - TASK-E001
**Completed By:** Executor  
**Date:** 2025-12-07  
**Status:** COMPLETE

---

## 1. FRED API Overview

**FRED** = Federal Reserve Economic Data  
**Host:** Federal Reserve Bank of St. Louis  
**Base URL:** `https://api.stlouisfed.org/fred`

### Key Features:
- **FREE** API access with registration
- 850,000+ data series available
- Real-time and historical data
- JSON and XML response formats
- Rate limit: 120 requests per minute (generous)

---

## 2. Registration Process

### Steps to Get API Key:
1. Go to: https://fred.stlouisfed.org/
2. Click "My Account" (top right)
3. Create account (free, email verification required)
4. After login: Go to https://fredaccount.stlouisfed.org/apikeys
5. Click "Request API Key"
6. Fill form (Purpose: "Financial Analysis Application")
7. Key is issued INSTANTLY (32-character string)

### API Key Format:
```
Example: 1234567890abcdef1234567890abcdef
```

---

## 3. Treasury Rate Endpoints

### Critical Series IDs for DCF/WACC:

| Series ID | Description | Use Case |
|-----------|-------------|----------|
| **DGS10** | 10-Year Treasury Constant Maturity Rate | Risk-free rate for WACC |
| **DGS5** | 5-Year Treasury Constant Maturity Rate | Alternative Rf |
| **DGS30** | 30-Year Treasury Constant Maturity Rate | Long-term projects |
| **DTB3** | 3-Month Treasury Bill Rate | Short-term Rf |
| **DFF** | Federal Funds Rate | Current Fed rate |
| **BAMLC0A0CM** | Corporate Bond Spread (Moody's Aaa) | Cost of Debt adjustment |

### Primary Endpoint:
```
GET https://api.stlouisfed.org/fred/series/observations
```

### Parameters:
| Parameter | Required | Description |
|-----------|----------|-------------|
| `series_id` | Yes | e.g., "DGS10" |
| `api_key` | Yes | Your API key |
| `file_type` | No | "json" (default) or "xml" |
| `observation_start` | No | "YYYY-MM-DD" |
| `observation_end` | No | "YYYY-MM-DD" |
| `sort_order` | No | "asc" or "desc" |

### Example Request:
```python
import requests

API_KEY = "your_api_key_here"
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key={API_KEY}&file_type=json&sort_order=desc&limit=1"

response = requests.get(url)
data = response.json()
latest_rate = float(data['observations'][0]['value']) / 100  # Convert to decimal
```

### Example Response:
```json
{
  "observations": [
    {
      "date": "2024-12-06",
      "value": "4.15"
    }
  ]
}
```

---

## 4. Python Integration Recommendations

### Suggested Implementation (`fred_api.py`):

```python
"""
FRED API Integration Module
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict

class FREDClient:
    BASE_URL = "https://api.stlouisfed.org/fred"
    
    # Cache TTL in seconds (1 hour recommended for treasury rates)
    CACHE_TTL = 3600
    
    # Treasury series mapping
    TREASURY_SERIES = {
        '10Y': 'DGS10',
        '5Y': 'DGS5',
        '30Y': 'DGS30',
        '3M': 'DTB3',
        'fed_funds': 'DFF'
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('FRED_API_KEY')
        if not self.api_key:
            raise ValueError("FRED API key required. Set FRED_API_KEY env var or pass directly.")
        self._cache = {}
    
    def get_treasury_rate(self, maturity: str = '10Y') -> float:
        """Get current treasury rate for given maturity."""
        series_id = self.TREASURY_SERIES.get(maturity, 'DGS10')
        return self._get_latest_value(series_id)
    
    def _get_latest_value(self, series_id: str) -> float:
        """Fetch latest observation for a series."""
        # Check cache first
        cache_key = f"{series_id}_latest"
        if cache_key in self._cache:
            cached_time, cached_value = self._cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.CACHE_TTL):
                return cached_value
        
        # Fetch from API
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': 5  # Get recent to handle missing days
        }
        
        response = requests.get(f"{self.BASE_URL}/series/observations", params=params)
        response.raise_for_status()
        
        data = response.json()
        for obs in data.get('observations', []):
            value = obs.get('value')
            if value and value != '.':  # FRED uses '.' for missing
                rate = float(value) / 100  # Convert percentage to decimal
                self._cache[cache_key] = (datetime.now(), rate)
                return rate
        
        raise ValueError(f"No valid data found for {series_id}")
```

---

## 5. Environment Setup

### Required:
1. Register at fred.stlouisfed.org
2. Get API key
3. Add to `.env`:
```
FRED_API_KEY=your_32_character_key_here
```

### Optional pip install:
```bash
pip install fredapi  # Alternative library (wraps the API)
```

---

## 6. Rate Limits & Best Practices

| Limit | Value |
|-------|-------|
| Requests/minute | 120 |
| Daily limit | None (but be respectful) |
| Concurrent | Unlimited |

### Best Practices:
1. **Cache responses** (rates don't change intraday)
2. **Use HTTPS** (required)
3. **Handle `.` values** (means data unavailable for that day)
4. **Fetch recent 5 days** (in case most recent is missing)

---

## 7. Next Steps for TASK-E007

With this research complete, TASK-E007 (implementation) can proceed:

1. Create `data_sources/fred_api.py`
2. Implement `FREDClient` class (see template above)
3. Add caching (1-hour TTL)
4. Wire to `dcf_modeling.py` for risk-free rate
5. Add to `config/app_config.py` API configuration

---

## 8. Action Items

- [x] Researched FRED API
- [x] Documented registration process
- [x] Identified treasury rate series IDs
- [x] Created implementation template
- [ ] **USER ACTION:** Register at fred.stlouisfed.org and get API key
- [ ] **ARCHITECT:** Proceed with TASK-E007 implementation using this research

---

**Research Complete. Ready for TASK-E007 implementation.**

