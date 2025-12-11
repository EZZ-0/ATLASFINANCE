# ATLAS Data Quality & Additions Plan

**Created:** December 10, 2025  
**Status:** Future Implementation (Low Capability / Free APIs)  
**Current Stack:** yfinance, SEC EDGAR, FRED API, Damodaran Data

---

## Executive Summary

Data quality improvements and additions achievable with current free API stack. No paid subscriptions required.

---

## 1. Data Quality Improvements (Free to Implement)

| Enhancement                    | Current State       | Improvement                                      | Effort |
|-------------------------------|---------------------|--------------------------------------------------|--------|
| **Stale Data Detection**       | None                | Add timestamp check, warn if data >7 days old   | Low    |
| **Data Freshness Badge**       | None                | Show "Last Updated: Dec 10, 2025" on each metric| Low    |
| **SEC vs yfinance Diff Alert** | Extraction only     | Show warning if sources differ >5%              | Medium |
| **Missing Data Fill Indicator**| Silent fallback     | Show which fields are estimated vs actual       | Low    |
| **NaN/Null Handling**          | Basic               | Consistent "N/A" display with tooltip reason    | Low    |
| **Data Source Attribution**    | None                | Badge showing "SEC", "yfinance", "Estimated"    | Low    |

---

## 2. Free Data Additions (Already Available)

### Currently Integrated but Underutilized

| Source           | What's Available                              | Current Usage        | Expansion Opportunity                |
|------------------|-----------------------------------------------|----------------------|--------------------------------------|
| **FRED API**     | 800k+ economic series                         | Partial (fred_api.py)| Add macro dashboard, sector rates    |
| **Damodaran**    | Industry betas, ERP, cost of capital          | DCF only             | Add industry comparison benchmarks   |
| **yfinance**     | Analyst ratings, recommendations, targets     | Price only           | Add consensus estimates section      |
| **SEC EDGAR**    | Insider transactions, institutional ownership | Extracted            | Better visualization, alerts         |

### New Free Sources to Add

| Source                  | Data Available                                    | Effort | Priority |
|-------------------------|---------------------------------------------------|--------|----------|
| **yfinance .info**      | Analyst recommendations, price targets            | Low    | HIGH     |
| **yfinance .recommendations** | Buy/Hold/Sell ratings history              | Low    | HIGH     |
| **FRED Treasury Rates** | Risk-free rate for DCF (live)                     | Low    | HIGH     |
| **FRED CPI/Inflation**  | Real vs nominal returns context                   | Low    | MEDIUM   |
| **FRED Sector Indices** | Sector performance benchmarking                   | Medium | MEDIUM   |
| **Yahoo Earnings Calendar** | Upcoming earnings dates                       | Low    | HIGH     |
| **Finviz (scraping)**   | Stock screener data (careful with ToS)            | Medium | LOW      |

---

## 3. Validation Engine Enhancements

### Current State (validation_engine.py)

Already has:
- Data format validation
- Range checks
- Consistency validation
- Reasonableness tests

### Additions Needed

| Validation                     | Purpose                                           | Implementation        |
|--------------------------------|---------------------------------------------------|-----------------------|
| **Year-over-Year Sanity**      | Flag if revenue changed >100% YoY                 | Add to reasonableness |
| **Margin Bounds**              | Flag if margins <-50% or >80%                     | Add to range checks   |
| **Historical Continuity**      | Flag gaps in quarterly data                       | New check             |
| **Cross-Statement Validation** | Net Income on IS = Net Income on CF               | New check             |
| **Dividend Sanity**            | Flag if payout ratio >150%                        | New check             |

---

## 4. Quick Wins (Implement in 1-2 Hours Each)

### Priority 1: Data Freshness Display

```python
# Add to each data section
st.caption(f"📅 Data as of: {data_timestamp.strftime('%Y-%m-%d %H:%M')} | Source: {source}")
```

### Priority 2: Analyst Estimates from yfinance

```python
# Already available in yfinance
ticker = yf.Ticker("AAPL")
recommendations = ticker.recommendations  # DataFrame with ratings
analyst_price_targets = ticker.analyst_price_targets  # Dict with low/mean/high
```

### Priority 3: Live Risk-Free Rate

```python
# From FRED (already have fred_api.py)
# Series: DGS10 (10-Year Treasury)
risk_free_rate = fred.get_series('DGS10').iloc[-1] / 100
```

### Priority 4: Earnings Calendar

```python
# From yfinance
ticker = yf.Ticker("AAPL")
calendar = ticker.calendar  # Next earnings date
```

---

## 5. Data Quality Dashboard Concept

Add a "Data Health" section showing:

```
┌─────────────────────────────────────────────────────┐
│  DATA QUALITY SCORECARD                             │
├─────────────────────────────────────────────────────┤
│  ✅ Financial Statements    Complete (SEC 10-K)     │
│  ✅ Price Data               Live (yfinance)        │
│  ⚠️  Insider Transactions   Partial (last 6mo)     │
│  ✅ Analyst Estimates        Available              │
│  ❌ Institutional Holdings   Missing Q4 data        │
│  ✅ Risk-Free Rate           Live (FRED DGS10)      │
├─────────────────────────────────────────────────────┤
│  Overall Data Confidence: 87%                       │
└─────────────────────────────────────────────────────┘
```

---

## 6. Implementation Roadmap

### Phase 1: Quick Wins (1 day)

- [ ] Add data freshness timestamps to all sections
- [ ] Add source attribution badges
- [ ] Integrate analyst estimates from yfinance
- [ ] Add live risk-free rate from FRED

### Phase 2: Validation Enhancements (2-3 days)

- [ ] Add YoY sanity checks
- [ ] Add cross-statement validation
- [ ] Add margin bounds checking
- [ ] Create data quality scorecard UI

### Phase 3: New Data Sources (1 week)

- [ ] Expand FRED integration (macro dashboard)
- [ ] Add earnings calendar display
- [ ] Add Damodaran industry benchmarks comparison
- [ ] Add sector performance context

---

## 7. What We DON'T Have (Paid Only)

| Feature                    | Why We Can't Add It                  | Workaround                      |
|---------------------------|--------------------------------------|---------------------------------|
| Real-time quotes          | yfinance has 15-min delay            | Show "delayed" disclaimer       |
| Level 2 order book        | Bloomberg/Refinitiv only             | None                            |
| Institutional 13F live    | WhaleWisdom/paid services            | SEC EDGAR quarterly             |
| Alternative data          | Satellites, credit cards             | None at free tier               |
| Consensus EPS estimates   | FactSet/Bloomberg                    | yfinance analyst targets        |
| Transcripts               | Seeking Alpha Premium                | None                            |

---

## Files to Modify When Implementing

| File                   | Changes                                            |
|------------------------|---------------------------------------------------|
| `usa_backend.py`       | Add analyst estimates fetching                    |
| `dashboard_tab.py`     | Add data freshness display                        |
| `dcf_modeling.py`      | Use live FRED risk-free rate                      |
| `data_sources/fred_api.py` | Expand series coverage                        |
| `validation_engine.py` | Add new validation checks                         |
| `flip_cards.py`        | Add source attribution badges                     |
| *New:* `data_quality.py` | Data health scorecard component                 |

---

## Notes

- All improvements use **existing free APIs**
- No breaking changes to current functionality
- Incremental implementation possible
- Focus on user-visible quality indicators



