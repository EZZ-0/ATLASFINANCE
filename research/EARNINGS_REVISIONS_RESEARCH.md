# Earnings Revisions Research - TASK-E011 & E012

**Completed By:** Executor  
**Date:** 2025-12-08  
**Status:** COMPLETE

---

## 1. Executive Summary

| Source | Revision Tracking | Quality | Cost |
|--------|-------------------|---------|------|
| yfinance | ⚠️ Limited | Good for current | Free |
| FMP | ✅ Full history | Excellent | Paid (freemium) |
| Alpha Vantage | ⚠️ Limited | Good | Free tier available |
| Zacks | ✅ Best-in-class | Excellent | Expensive |

**Recommendation:** Use **yfinance** for current estimates + **FMP** for revision history.

---

## 2. TASK-E011: yfinance Earnings Fields

### 2.1 Available Data

#### `stock.earnings_dates` DataFrame

| Column | Description | Available |
|--------|-------------|-----------|
| `EPS Estimate` | Analyst consensus EPS estimate | ✅ |
| `Reported EPS` | Actual reported EPS | ✅ |
| `Surprise(%)` | Surprise percentage | ✅ |
| Index | Earnings date | ✅ |

**Sample Code:**
```python
import yfinance as yf

stock = yf.Ticker("AAPL")
earnings = stock.earnings_dates

# Returns DataFrame:
#                     EPS Estimate  Reported EPS  Surprise(%)
# 2024-10-31                  1.60          1.64         2.50
# 2024-07-25                  1.35          1.40         3.70
# 2024-05-02                  1.50          1.53         2.00
```

#### `stock.earnings_history` DataFrame

| Column | Description |
|--------|-------------|
| `epsEstimate` | Analyst estimate at time of report |
| `epsActual` | Reported EPS |
| `epsDifference` | Actual - Estimate |
| `surprisePercent` | Percentage beat/miss |

#### `stock.info` Fields

| Field | Description |
|-------|-------------|
| `forwardEps` | Consensus forward EPS |
| `trailingEps` | TTM EPS |
| `targetMeanPrice` | Mean analyst price target |
| `targetHighPrice` | High price target |
| `targetLowPrice` | Low price target |
| `numberOfAnalystOpinions` | Analyst coverage count |
| `recommendationKey` | Buy/Hold/Sell consensus |
| `recommendationMean` | 1-5 scale recommendation |

#### `stock.recommendations` DataFrame

| Column | Description |
|--------|-------------|
| `Firm` | Analyst firm name |
| `To Grade` | New rating |
| `From Grade` | Previous rating |
| `Action` | Upgrade/Downgrade/Initiate |

### 2.2 Limitations of yfinance

| Gap | Impact | Alternative |
|-----|--------|-------------|
| **No revision history** | Can't track estimate changes over time | FMP API |
| **No revision dates** | Can't see when estimates were revised | FMP API |
| **Limited analyst detail** | Only aggregate, not individual | FMP API |
| **No revenue estimates** | Only EPS estimates available | FMP API |

### 2.3 What yfinance CAN Do

1. ✅ Get current EPS estimates (forward/trailing)
2. ✅ Get historical surprises (beat/miss)
3. ✅ Get analyst recommendations
4. ✅ Get price targets
5. ✅ Calculate beat rate
6. ❌ Cannot track revision trends
7. ❌ Cannot show estimate evolution

---

## 3. TASK-E012: FMP/Alpha Vantage APIs

### 3.1 Financial Modeling Prep (FMP) - RECOMMENDED

**Endpoint:** `/analyst-estimates/{ticker}`

**Returns:**
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

**Historical Estimates:** `/analyst-estimates/{ticker}?period=annual&limit=10`

**Grade History:** `/grade/{ticker}`

| Field | Description |
|-------|-------------|
| `symbol` | Ticker |
| `date` | Grade date |
| `gradingCompany` | Analyst firm |
| `previousGrade` | Old rating |
| `newGrade` | New rating |

**FMP Pricing:**
- Free: 250 calls/day
- Basic: $19/mo - 300 calls/min
- Professional: $49/mo - 750 calls/min

### 3.2 Alpha Vantage - Limited

**Endpoint:** `EARNINGS`

**Returns:**
- Annual earnings (reported vs estimated)
- Quarterly earnings
- Limited to actual vs. estimate at report time

**Limitations:**
- No revision history
- No estimate evolution
- Limited analyst data

**Alpha Vantage Pricing:**
- Free: 25 calls/day
- Premium: $49/mo - 120 calls/min

### 3.3 Comparison Matrix

| Feature | yfinance | FMP | Alpha Vantage |
|---------|----------|-----|---------------|
| Current EPS Estimate | ✅ | ✅ | ✅ |
| Revenue Estimates | ❌ | ✅ | ❌ |
| Estimate History | ❌ | ✅ | ❌ |
| Revision Dates | ❌ | ✅ | ❌ |
| Analyst Grades | ✅ | ✅ | ❌ |
| Price Targets | ✅ | ✅ | ❌ |
| Free Tier | ✅ Unlimited | ✅ 250/day | ✅ 25/day |

---

## 4. Existing ATLAS Infrastructure

### 4.1 Current Implementation

Found `earnings_analysis.py` with:
- `analyze_earnings_history()` - Beat/miss analysis
- `get_earnings_calendar()` - Upcoming dates
- EPS trend analysis
- Earnings quality scoring

### 4.2 Gaps to Fill

| Gap | Solution |
|-----|----------|
| Revision trend tracking | Add FMP integration |
| Historical estimate data | Store in cache |
| Revision momentum indicator | Calculate from FMP data |
| UI display | Architect creating earnings_revisions.py |

---

## 5. Recommended Implementation

### 5.1 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    EARNINGS REVISIONS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. CURRENT DATA (yfinance)                                 │
│     └── Forward EPS, Trailing EPS, Price Target             │
│                                                             │
│  2. HISTORICAL ESTIMATES (FMP API)                          │
│     └── Estimate evolution over 30/60/90 days               │
│                                                             │
│  3. GRADE HISTORY (FMP API)                                 │
│     └── Analyst upgrades/downgrades                         │
│                                                             │
│  4. REVISION MOMENTUM                                       │
│     └── Direction: ↑ Up / ↓ Down / → Stable                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Key Metrics to Display

| Metric | Source | Description |
|--------|--------|-------------|
| EPS Revision (30D) | FMP | % change in consensus EPS |
| Revenue Revision (30D) | FMP | % change in consensus revenue |
| Analyst Upgrades | FMP | Count of upgrades |
| Analyst Downgrades | FMP | Count of downgrades |
| Net Rating Change | FMP | Upgrades - Downgrades |
| Revision Trend | Calc | Bullish/Neutral/Bearish |

### 5.3 Python Implementation Skeleton

```python
class EarningsRevisionTracker:
    """Track analyst estimate revisions over time."""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.yf_data = self._get_yfinance_data()
        self.fmp_data = self._get_fmp_data() if FMP_API_KEY else None
    
    def get_current_estimates(self) -> Dict:
        """Get current consensus estimates from yfinance."""
        return {
            'forward_eps': self.yf_data.get('forwardEps'),
            'trailing_eps': self.yf_data.get('trailingEps'),
            'target_price': self.yf_data.get('targetMeanPrice'),
            'analyst_count': self.yf_data.get('numberOfAnalystOpinions'),
        }
    
    def get_revision_trend(self, days: int = 30) -> Dict:
        """Get estimate revision over specified period."""
        if not self.fmp_data:
            return {'status': 'unavailable', 'reason': 'FMP API key required'}
        
        # Calculate revision % from FMP historical data
        return {
            'eps_revision_pct': self._calc_eps_revision(days),
            'revenue_revision_pct': self._calc_revenue_revision(days),
            'direction': self._get_direction(),
            'momentum': self._calc_momentum(),
        }
    
    def get_analyst_changes(self, days: int = 90) -> Dict:
        """Get analyst rating changes."""
        # Use FMP grade endpoint
        return {
            'upgrades': count_upgrades,
            'downgrades': count_downgrades,
            'initiations': count_initiations,
            'net_change': upgrades - downgrades,
        }
```

---

## 6. API Key Requirements

### 6.1 FMP Registration

1. Go to: https://financialmodelingprep.com/developer/docs/
2. Create account (free)
3. Get API key (250 calls/day free)
4. Set env: `FMP_API_KEY=your_key`

### 6.2 Current ATLAS Config

Check `config/app_config.py`:
```python
FMP_API_KEY = os.getenv('FMP_API_KEY', '')
```

Already supports FMP! Just need API key set.

---

## 7. Validation Notes

### 7.1 Data Quality Checks

| Check | Method |
|-------|--------|
| EPS estimate reasonable | Within 50% of trailing |
| Revision % capped | Limit to ±100% |
| Date validity | Within 2 years |
| Analyst count | Minimum 3 for reliability |

### 7.2 Edge Cases

| Case | Handling |
|------|----------|
| No FMP key | Fall back to yfinance only |
| No estimates available | Show "N/A - No coverage" |
| Single analyst | Flag as "Low confidence" |
| IPO/new stock | Limited history warning |

---

## 8. Conclusion

### TASK-E011 (yfinance) - COMPLETE ✅

**Available Fields:**
- `earnings_dates`: EPS estimates, reported, surprises
- `earnings_history`: Historical beat/miss
- `info`: Forward EPS, targets, analyst count
- `recommendations`: Rating changes

**Limitation:** No revision history tracking.

### TASK-E012 (FMP/AV) - COMPLETE ✅

**Recommended:** FMP API for revision tracking:
- Historical estimates endpoint
- Analyst grades endpoint
- 250 free calls/day

**Implementation:** Architect building `earnings_revisions.py` module.

---

**Next Steps:**
- E013: Validate AAPL revision data
- E014: Validate MSFT revision data
- E015: Create tests after A007/A008 complete

