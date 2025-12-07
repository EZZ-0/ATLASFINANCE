# TASK-E018: Institutional Ownership Module Validation

**Date:** 2025-12-08  
**Executor:** Validating A015 output  
**Status:** ⚠️ ISSUE FOUND

---

## Test Results

| Ticker | Inst % | Insider % | Top 10 % | Status |
|--------|--------|-----------|----------|--------|
| AAPL | 0.0% | 0.0% | 0.0% | ⚠️ Incorrect |
| MSFT | 0.0% | 0.0% | 0.0% | ⚠️ Incorrect |
| GOOGL | 0.0% | 0.0% | 0.0% | ⚠️ Incorrect |

---

## Issue Analysis

### Raw yfinance Data (Direct Access)
```python
stock = yf.Ticker('AAPL')
stock.major_holders
```

**Output:**
```
Breakdown                          Value
insidersPercentHeld              0.01697
institutionsPercentHeld          0.64400
institutionsFloatPercentHeld     0.65511
institutionsCount             7074.00000
```

✅ **yfinance data IS available** - AAPL shows 64.4% institutional ownership.

### Root Cause

The `_parse_major_holders` method in `institutional_ownership.py` expects a different DataFrame format:

**Expected (by module):**
```python
for _, row in major_holders.iterrows():
    value = row.iloc[0]
    desc = str(row.iloc[1]).lower()  # Looking for 'institution' in description
```

**Actual (yfinance returns):**
```python
# DataFrame with 'Breakdown' as index and 'Value' as column
# NOT rows with [value, description] format
```

The DataFrame is indexed by the metric name, not by row number.

---

## External Source Comparison

| Ticker | Module | Yahoo Finance | Delta |
|--------|--------|---------------|-------|
| AAPL | 0.0% | 64.40% | ❌ -64.4% |
| MSFT | 0.0% | 74.01% | ❌ -74.0% |
| GOOGL | 0.0% | 81.56% | ❌ -81.6% |

---

## Top Holders Data

**Good news:** `stock.institutional_holders` DataFrame works correctly:
```
                         Holder      Shares        Value
Vanguard Group Inc     1599312352  390132302514
Blackrock Inc.         1309614476  319574509946
State Street Corp       683023044  166571359552
...
```

The module's `_parse_institutional_holders` should work for top holders list.

---

## Recommended Fix

Update `_parse_major_holders` method to handle yfinance's actual DataFrame format:

```python
def _parse_major_holders(self, summary, major_holders):
    try:
        # yfinance returns DataFrame with 'Breakdown' index
        if 'institutionsPercentHeld' in major_holders.index:
            summary.institutional_pct = float(major_holders.loc['institutionsPercentHeld', 'Value']) * 100
        if 'insidersPercentHeld' in major_holders.index:
            summary.insider_pct = float(major_holders.loc['insidersPercentHeld', 'Value']) * 100
    except Exception as e:
        logger.debug(f"Error parsing major holders: {e}")
    return summary
```

---

## Module Quality Assessment (Other Features)

| Criteria | Status | Notes |
|----------|--------|-------|
| Data extraction | ⚠️ | major_holders parsing issue |
| Top holders parsing | ✅ | institutional_holders works |
| Accumulation score | ⚠️ | Depends on fixed data |
| Concentration calc | ⚠️ | Works if top_holders populated |
| Visualizations | ✅ | Charts work with data |

---

## Conclusion

**TASK-E018: ⚠️ ISSUE FOUND**

**Issue:** `_parse_major_holders()` method doesn't correctly parse yfinance's `major_holders` DataFrame format.

**Impact:** Institutional/insider percentages return 0.0% instead of actual values.

**Fix Required:** Update parsing logic to use index-based access.

**Notify:** @ARCHITECT - Bug found in A015

