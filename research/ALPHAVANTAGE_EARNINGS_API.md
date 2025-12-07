# Alpha Vantage Earnings API Research

**Task:** E013  
**Completed By:** Executor  
**Date:** 2025-12-08  
**Status:** COMPLETE ✅

---

## 1. Summary

| Feature | Available | Quality |
|---------|-----------|---------|
| Current EPS Estimates | ⚠️ Limited | Fair |
| Revenue Estimates | ❌ No | N/A |
| Historical Estimates | ❌ No | N/A |
| Revision Dates | ❌ No | N/A |
| Actual vs Estimated | ✅ Yes | Good |
| Earnings Calendar | ❌ No | N/A |

**Bottom Line:** Alpha Vantage is NOT recommended for revision tracking. Limited earnings data.

---

## 2. Alpha Vantage Overview

**Base URL:** `https://www.alphavantage.co/query`

**Authentication:** API key required (`&apikey=YOUR_KEY`)

**Free Tier:** 25 calls/day (5 calls/minute)

**Documentation:** https://www.alphavantage.co/documentation/

---

## 3. EARNINGS Endpoint

**Endpoint:** `EARNINGS`

**URL Format:**
```
https://www.alphavantage.co/query?function=EARNINGS&symbol=AAPL&apikey=YOUR_KEY
```

**Response Structure:**
```json
{
  "symbol": "AAPL",
  "annualEarnings": [
    {
      "fiscalDateEnding": "2024-09-30",
      "reportedEPS": "6.42"
    },
    {
      "fiscalDateEnding": "2023-09-30",
      "reportedEPS": "5.97"
    }
  ],
  "quarterlyEarnings": [
    {
      "fiscalDateEnding": "2024-09-30",
      "reportedDate": "2024-10-31",
      "reportedEPS": "1.64",
      "estimatedEPS": "1.60",
      "surprise": "0.04",
      "surprisePercentage": "2.50"
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `fiscalDateEnding` | string | Fiscal period end date |
| `reportedDate` | string | Actual earnings report date |
| `reportedEPS` | string | Actual reported EPS |
| `estimatedEPS` | string | Consensus estimate at report time |
| `surprise` | string | EPS beat/miss amount |
| `surprisePercentage` | string | Surprise as percentage |

---

## 4. What Alpha Vantage CAN Do

✅ **Available:**
- Historical reported EPS (annual and quarterly)
- EPS estimate at time of report
- Surprise calculation (beat/miss)
- Report dates

**Use Case:** Beat/miss analysis (similar to yfinance.earnings_dates)

---

## 5. What Alpha Vantage CANNOT Do

❌ **NOT Available:**
- Historical estimate changes (revision tracking)
- Revenue estimates
- Analyst grade changes
- Price targets
- Individual analyst estimates
- Estimate dispersion
- Forward estimates

**Major Limitation:** Only provides estimate AT TIME OF REPORT, not estimate EVOLUTION.

---

## 6. Rate Limits & Pricing

| Plan | Calls/Day | Calls/Min | Price |
|------|-----------|-----------|-------|
| Free | 25 | 5 | $0 |
| Premium | Varies | 120 | $49/mo+ |

**For ATLAS:**
- Free tier too restrictive (only 25/day)
- Not cost-effective for revision tracking
- Better alternatives exist (FMP)

---

## 7. API Key Availability

### Check for Existing Key

Search in project:
```bash
# Check .env files
grep -r "ALPHA" .env*
grep -r "ALPHAVANTAGE" config/
```

**Current Status:** No Alpha Vantage key found in project.

### Getting Free Key

1. Go to: https://www.alphavantage.co/support/#api-key
2. Enter email
3. Receive key immediately
4. Free tier: 25 calls/day

---

## 8. Sample API Call

```python
import requests
import os

AV_API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

def get_av_earnings(ticker: str):
    """Get earnings data from Alpha Vantage."""
    if not AV_API_KEY:
        return None
        
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'EARNINGS',
        'symbol': ticker,
        'apikey': AV_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        return {
            'annual': data.get('annualEarnings', []),
            'quarterly': data.get('quarterlyEarnings', [])
        }
    return None
```

---

## 9. Comparison with Other Sources

| Feature | yfinance | FMP | Alpha Vantage |
|---------|----------|-----|---------------|
| Current EPS | ✅ | ✅ | ⚠️ |
| Forward Estimates | ✅ | ✅ | ❌ |
| Revenue Estimates | ❌ | ✅ | ❌ |
| Revision History | ❌ | ✅ | ❌ |
| Beat/Miss Data | ✅ | ✅ | ✅ |
| Analyst Grades | ✅ | ✅ | ❌ |
| Free Calls/Day | Unlimited | 250 | 25 |
| Rate Limit | None | 5/min | 5/min |

---

## 10. Integration Decision

### NOT Recommended for ATLAS

**Reasons:**
1. **Limited Data:** Only beat/miss, no revision tracking
2. **Restrictive Free Tier:** 25 calls/day is too low
3. **Better Alternatives:** yfinance (free) + FMP (250/day)
4. **No Unique Value:** Nothing AV provides that others don't

### If Still Needed

Could be used as tertiary fallback:
```python
def get_earnings_data(ticker: str):
    """Get earnings with fallback chain."""
    # 1. Try yfinance (free, unlimited)
    data = get_yfinance_earnings(ticker)
    if data:
        return data
    
    # 2. Try FMP (free tier 250/day)
    data = get_fmp_earnings(ticker)
    if data:
        return data
    
    # 3. Try Alpha Vantage (free tier 25/day) - LAST RESORT
    data = get_av_earnings(ticker)
    if data:
        return data
    
    return None
```

---

## 11. Conclusion

**Alpha Vantage is NOT suitable for earnings revision tracking because:**

❌ No historical estimate evolution
❌ No revenue estimates
❌ No analyst grade changes
❌ Very restrictive free tier (25/day)
❌ No forward estimates
❌ No unique data vs. yfinance

**Recommendation:** 
- **Skip Alpha Vantage** for this feature
- Use **yfinance** (primary) + **FMP** (revision history)
- No need to add another API dependency

**If Alpha Vantage key available:** Could use for basic beat/miss validation, but not worth the integration effort given rate limits.

