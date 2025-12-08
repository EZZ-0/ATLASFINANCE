# TASK-E020: 13F Institutional Holdings Research

**Date:** 2025-12-08  
**Executor:** Research for A017 (13F Integration)  
**Status:** ✅ COMPLETE

---

## What is Form 13F?

**SEC Form 13F** is a quarterly filing required by institutional investment managers with at least $100M in AUM. It discloses their equity holdings.

- **Filing Deadline:** 45 days after quarter end
- **Required Filers:** Hedge funds, mutual funds, pension funds, etc.
- **Content:** Long equity positions (stocks, ETFs, some options)
- **Excluded:** Short positions, bonds, non-US securities

---

## Data Sources Comparison

### 1. SEC EDGAR (Official)

**Endpoint:** `https://data.sec.gov/submissions/CIK{cik}.json`

**Pros:**
- Official source
- Free, no API key
- Includes all 13F filings

**Cons:**
- Raw XML/text parsing required
- No pre-aggregated holdings by stock
- Need to download individual filing documents
- Complex to aggregate all filers for a given stock

**Use Case:** Best for tracking a SPECIFIC institution's holdings.

---

### 2. yfinance `institutional_holders`

**Method:** `stock.institutional_holders`

**Returns DataFrame:**
```
Holder           Shares      Value         pctChange
Vanguard         1599M       $390B         -1.17%
Blackrock        1309M       $319B         -0.22%
...
```

**Pros:**
- Already integrated
- Pre-aggregated by stock
- Includes top 10-15 holders
- Has pctChange field (!)

**Cons:**
- Limited to top holders only
- Not full 13F data
- Date Reported may be stale
- No historical tracking

**Use Case:** ✅ BEST for quick ownership overview.

---

### 3. WhaleWisdom

**Website:** whalewisdom.com

**Pros:**
- Excellent 13F aggregation
- Historical tracking
- New/increased/decreased positions
- Heat maps and analysis

**Cons:**
- No public API
- Paid subscription required
- Would need scraping (ToS issue)

**Use Case:** Manual research only (not for automation).

---

### 4. Fintel

**Website:** fintel.io

**Pros:**
- Good 13F tracking
- Some free data
- API available (paid)

**Cons:**
- Expensive API ($200+/month)
- Free tier very limited

**Use Case:** Not recommended for this project.

---

### 5. FMP API

**Endpoint:** `/institutional-holder/{ticker}`

**Response Sample:**
```json
[
  {
    "holder": "Vanguard Group Inc",
    "shares": 1599312352,
    "dateReported": "2024-09-30",
    "change": -18965372,
    "changePercentage": -1.17
  }
]
```

**Pros:**
- Clean JSON format
- Change data included
- Historical available (premium)

**Cons:**
- 250 calls/day free tier
- Full history requires paid plan

**Use Case:** ✅ GOOD supplement to yfinance.

---

## Recommended Implementation

### Primary: yfinance `institutional_holders`

```python
stock = yf.Ticker(ticker)
holders = stock.institutional_holders

# Returns DataFrame with:
# - Holder name
# - Shares
# - Value
# - Date Reported
# - % Change (from previous quarter!)
```

**Key Finding:** yfinance already includes `pctChange` column!

This means we CAN detect accumulation/distribution without additional APIs.

### Secondary: FMP API (Optional Enhancement)

Use FMP's `/institutional-holder/{ticker}` for:
- More detailed change history
- Additional holder metadata
- Validation/backup data

---

## Quarterly Ownership Changes

### Available in yfinance:

| Field | Description |
|-------|-------------|
| `pctChange` | Change vs previous quarter |
| `Date Reported` | Filing date (usually Q-end + 45d) |

### Interpretation:

| pctChange | Meaning |
|-----------|---------|
| > 5% | Accumulating |
| -5% to 5% | Holding |
| < -5% | Distributing |

---

## Implementation Recommendations for A017

1. **Use yfinance as primary source** - Already integrated, has change data

2. **Parse `pctChange` column** to calculate accumulation score

3. **Track new/exited positions** by comparing holder lists

4. **Optional FMP integration** for richer history

5. **No need for SEC EDGAR parsing** - yfinance provides sufficient data

---

## Data Freshness

- **13F Filing Deadline:** 45 days after quarter end
- **Q3 2024 filings:** Due November 14, 2024
- **yfinance Update Frequency:** Within days of SEC filings

---

## Conclusion

**Best Approach:** Use yfinance's existing `institutional_holders` DataFrame.

The `pctChange` column already provides quarter-over-quarter change data, which is sufficient for accumulation/distribution analysis.

**No additional API needed** for basic 13F tracking.

For advanced features (full holder history, precise dates), FMP API is the best supplement.

