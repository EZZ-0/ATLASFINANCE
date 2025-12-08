# SEC EDGAR Insider Transaction Research

**Task:** TASK-A014 (Architect)  
**Created:** 2025-12-08  
**Purpose:** Research SEC EDGAR API for Form 4 insider transactions

---

## Overview

SEC Form 4 is the mandatory filing insiders must submit within 2 business days of a transaction.

**Insiders include:**
- Officers (CEO, CFO, COO, etc.)
- Directors
- 10%+ beneficial owners

---

## SEC EDGAR API Endpoints

### 1. Company Submissions API

**Endpoint:** `https://data.sec.gov/submissions/CIK{cik}.json`

**Example:** `https://data.sec.gov/submissions/CIK0000320193.json` (Apple)

**Response includes:**
- All recent filings (10-K, 10-Q, 8-K, 4, etc.)
- Filing dates, accession numbers
- Links to documents

**Rate Limit:** 10 requests per second (with User-Agent header)

### 2. Full-Text Search API

**Endpoint:** `https://efts.sec.gov/LATEST/search-index`

**Use for:** Searching across filings by keyword

### 3. XBRL Data API

**Endpoint:** `https://data.sec.gov/api/xbrl/`

**Use for:** Structured financial data

---

## Form 4 Structure

Form 4 filings contain:

1. **Reporting Owner Info**
   - Name
   - CIK
   - Relationship to issuer (Officer, Director, 10% Owner)
   - Officer title

2. **Transaction Details** (Table 1 - Non-Derivative)
   - Security title
   - Transaction date
   - Transaction code (P=Purchase, S=Sale, etc.)
   - Shares acquired/disposed
   - Price per share
   - Shares owned after transaction

3. **Derivative Securities** (Table 2)
   - Options, warrants, convertibles
   - Exercise price
   - Expiration date

---

## Transaction Codes

| Code | Meaning |
|------|---------|
| P | Purchase |
| S | Sale |
| A | Award/Grant |
| M | Option Exercise |
| C | Conversion |
| G | Gift |
| F | Tax withholding |
| I | Discretionary transaction |

---

## Implementation Strategy

### Option A: Direct SEC EDGAR API (Recommended)

**Pros:**
- Official source
- Free, no API key needed
- Comprehensive data
- Real-time (2-day delay from transaction)

**Cons:**
- Need to parse XML/JSON
- Need company CIK mapping
- Rate limiting

**Implementation:**
```python
import requests

def get_form4_filings(cik: str) -> list:
    """Get Form 4 filings from SEC EDGAR."""
    url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    headers = {
        'User-Agent': 'ATLAS Financial Intelligence contact@example.com'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Filter for Form 4 filings
    filings = data['filings']['recent']
    form4_indices = [i for i, form in enumerate(filings['form']) if form == '4']
    
    return [{
        'accession': filings['accessionNumber'][i],
        'filing_date': filings['filingDate'][i],
        'primary_doc': filings['primaryDocument'][i]
    } for i in form4_indices]
```

### Option B: OpenInsider Scraping

**Pros:**
- Pre-parsed data
- Easy to use
- Includes historical data

**Cons:**
- Unofficial
- May break if site changes
- Terms of service concerns

### Option C: yfinance (Current)

**Pros:**
- Already integrated
- Easy to use

**Cons:**
- Limited data
- May not update quickly
- Missing some fields

---

## CIK Mapping

Need to map ticker to CIK for SEC API:

**Option 1:** SEC company_tickers.json
```python
url = "https://www.sec.gov/files/company_tickers.json"
# Returns: {ticker: cik} mapping
```

**Option 2:** Build local mapping
```python
TICKER_CIK_MAP = {
    'AAPL': '0000320193',
    'MSFT': '0000789019',
    'GOOGL': '0001652044',
    # ... etc
}
```

---

## Recommended Next Steps

1. **Use yfinance as primary** (already working)
2. **Add SEC EDGAR as fallback/enhancement** for:
   - More detailed transaction data
   - Official filing dates
   - Derivative transactions
3. **Cache SEC data aggressively** (24-hour TTL)
4. **Create CIK mapping module** for major tickers

---

## Sample SEC API Response

```json
{
  "cik": "320193",
  "entityType": "operating",
  "sic": "3571",
  "sicDescription": "Electronic Computers",
  "name": "Apple Inc.",
  "tickers": ["AAPL"],
  "filings": {
    "recent": {
      "accessionNumber": ["0001193125-24-123456", ...],
      "filingDate": ["2024-01-15", ...],
      "form": ["4", "10-K", "8-K", ...],
      "primaryDocument": ["xslForm4.xml", ...]
    }
  }
}
```

---

## Testing

```python
# Test SEC API access
import requests

url = "https://data.sec.gov/submissions/CIK0000320193.json"
headers = {'User-Agent': 'Test contact@test.com'}
response = requests.get(url, headers=headers)
print(response.status_code)  # Should be 200
```

---

## Conclusion

**Recommendation:** Enhance `insider_transactions.py` with:
1. Keep yfinance as primary (fast, simple)
2. Add SEC EDGAR fallback (official, detailed)
3. Create `sec_edgar.py` module for reusable SEC API access
4. Cache aggressively to respect rate limits

**Priority:** Medium - Current yfinance implementation works, SEC adds depth.

