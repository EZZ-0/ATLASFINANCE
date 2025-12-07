# yfinance Earnings Fields Research

**Task:** E011  
**Completed By:** Executor  
**Date:** 2025-12-08  
**Status:** COMPLETE ✅

---

## 1. Summary

| Attribute | Type | Data Available | Revision Tracking |
|-----------|------|----------------|-------------------|
| `earnings_dates` | DataFrame | ✅ Excellent | ❌ No |
| `earnings_history` | DataFrame | ✅ Good | ❌ No |
| `info` (EPS fields) | Dict | ✅ Excellent | ❌ No |
| `recommendations` | DataFrame | ✅ Good | ❌ No |
| `analyst_price_targets` | Dict | ✅ Good | ❌ No |
| `upgrades_downgrades` | DataFrame | ✅ Good | ❌ No |
| `calendar` | Dict | ✅ Good | ❌ No |

**Bottom Line:** yfinance provides excellent CURRENT data but NO historical revision tracking.

---

## 2. `stock.earnings_dates` DataFrame

**Description:** Historical and upcoming earnings dates with estimates and results.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| Index (Date) | DatetimeIndex | Earnings report date |
| `EPS Estimate` | float | Consensus analyst estimate |
| `Reported EPS` | float | Actual reported EPS |
| `Surprise(%)` | float | Beat/miss percentage |

**Sample Output (AAPL):**
```
                     EPS Estimate  Reported EPS  Surprise(%)
2024-10-31                  1.60          1.64         2.50
2024-07-25                  1.35          1.40         3.70
2024-05-02                  1.50          1.53         2.00
2024-02-01                  2.10          2.18         3.80
```

**Use Cases:**
- Calculate beat/miss rate
- Track earnings history
- Identify surprise trends

---

## 3. `stock.earnings_history` DataFrame

**Description:** Detailed earnings history with estimates and actuals.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| `epsEstimate` | float | Analyst consensus at time |
| `epsActual` | float | Reported EPS |
| `epsDifference` | float | Actual - Estimate |
| `surprisePercent` | float | Percentage beat/miss |

---

## 4. `stock.info` Dictionary (EPS Fields)

**Description:** Current snapshot of analyst estimates and metrics.

| Field | Description | Sample Value (AAPL) |
|-------|-------------|---------------------|
| `forwardEps` | Forward consensus EPS | 8.31 |
| `trailingEps` | TTM EPS | 7.47 |
| `targetMeanPrice` | Mean analyst price target | $255.00 |
| `targetHighPrice` | Highest price target | $300.00 |
| `targetLowPrice` | Lowest price target | $180.00 |
| `numberOfAnalystOpinions` | Count of analysts | 41 |
| `recommendationKey` | Consensus recommendation | "buy" |
| `recommendationMean` | 1-5 scale (1=Strong Buy) | 2.0 |
| `earningsGrowth` | YoY earnings growth | 0.15 (15%) |
| `earningsQuarterlyGrowth` | QoQ growth | 0.08 (8%) |

**Verification Test (Successful):**
```
forwardEps: 8.31
trailingEps: 7.47
numberOfAnalystOpinions: 41
```

---

## 5. `stock.recommendations` DataFrame

**Description:** Analyst rating changes over time.

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| Index (Date) | DatetimeIndex | Date of recommendation |
| `Firm` | str | Analyst firm name |
| `To Grade` | str | New rating |
| `From Grade` | str | Previous rating |
| `Action` | str | upgrade/downgrade/init/maintain |

**Sample:**
```
                 Firm       To Grade    From Grade    Action
2024-12-01    Morgan Stanley   Overweight  Overweight   maintain
2024-11-15    JP Morgan        Neutral     Neutral      maintain
2024-11-01    Baird            Outperform  Neutral      upgrade
```

---

## 6. `stock.analyst_price_targets` Dict

**Description:** Summary of analyst price targets.

**Fields:**
| Field | Description |
|-------|-------------|
| `current` | Current price |
| `low` | Lowest target |
| `high` | Highest target |
| `mean` | Mean target |
| `median` | Median target |

---

## 7. `stock.upgrades_downgrades` DataFrame

**Description:** Recent rating changes by firm.

**Columns:**
- `GradeDate`: Date of change
- `Firm`: Analyst firm
- `ToGrade`: New rating
- `FromGrade`: Previous rating
- `Action`: Type of change

---

## 8. `stock.calendar` Dict

**Description:** Next earnings date and dividend info.

**Fields:**
| Field | Description |
|-------|-------------|
| `Earnings Date` | Next earnings report date |
| `Earnings Average` | Consensus estimate |
| `Earnings Low` | Low estimate |
| `Earnings High` | High estimate |
| `Revenue Average` | Revenue estimate |
| `Ex-Dividend Date` | Next dividend date |

---

## 9. Limitations

| Gap | Impact | Workaround |
|-----|--------|------------|
| **No revision history** | Can't track how estimates changed over 30/60/90 days | Use FMP API |
| **No revision dates** | Can't see when specific analysts revised | Use FMP API |
| **Only aggregate data** | No individual analyst estimates | Use FMP API |
| **No revenue estimates in earnings_dates** | Only EPS estimates | Use FMP API |
| **Point-in-time snapshot** | Data only reflects current state | Cache historical snapshots |

---

## 10. What yfinance CAN Do for Revisions

✅ **Available:**
- Current EPS estimates (forward/trailing)
- Historical surprises (beat/miss rate)
- Analyst recommendations count
- Price targets (high/mean/low)
- Rating changes (upgrades/downgrades)
- Next earnings date

❌ **NOT Available:**
- Estimate changes over time
- 7-day / 30-day / 60-day / 90-day revision %
- Individual analyst estimates
- Revenue estimate history
- Estimate dispersion trends

---

## 11. Recommended Usage

```python
import yfinance as yf

def get_yfinance_earnings_data(ticker: str) -> dict:
    """Get all available earnings data from yfinance."""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    return {
        'current_estimates': {
            'forward_eps': info.get('forwardEps'),
            'trailing_eps': info.get('trailingEps'),
            'earnings_growth': info.get('earningsGrowth'),
        },
        'price_targets': {
            'mean': info.get('targetMeanPrice'),
            'high': info.get('targetHighPrice'),
            'low': info.get('targetLowPrice'),
        },
        'analyst_info': {
            'count': info.get('numberOfAnalystOpinions'),
            'rating': info.get('recommendationKey'),
            'rating_score': info.get('recommendationMean'),
        },
        'earnings_history': stock.earnings_dates,
        'recommendations': stock.recommendations,
    }
```

---

## 12. Conclusion

**yfinance is EXCELLENT for:**
- Getting current analyst consensus
- Calculating beat/miss rates
- Tracking rating changes
- Price target analysis

**yfinance CANNOT provide:**
- Revision momentum tracking
- Estimate evolution over time
- This requires FMP API integration

**Recommendation:** Use yfinance as primary source + FMP for revision history.

