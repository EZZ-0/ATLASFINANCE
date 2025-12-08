---
name: Full Metal Audit
overview: A phased approach to fix critical bugs first, wire dead features, consolidate duplicates, then gradually migrate to clean architecture while keeping the app functional at each step.
todos:
  - id: phase1-cagr
    content: Add Total_Assets and EPS CAGR to calculate_growth_rates()
    status: completed
  - id: phase1-sec-growth
    content: Call calculate_growth_rates() after SEC extraction
    status: completed
  - id: phase1-normalize
    content: Add DataFrame index normalization for SEC format
    status: completed
  - id: phase1-cache
    content: Reduce cache TTL to 5 min for testing
    status: completed
  - id: phase2-insider
    content: Wire Insider Transactions from dead code to Risk tab
    status: completed
  - id: phase2-ownership
    content: Wire Institutional Ownership from dead code to Risk tab
    status: completed
  - id: phase2-earnings
    content: Wire Earnings Revisions to Valuation tab
    status: completed
  - id: phase2-delete-dead
    content: Delete render_model_tab_EXAMPLE() function
    status: completed
  - id: phase3-flip-audit
    content: Audit and consolidate 4 flip card files into 1
    status: completed
  - id: phase4-tab-cleanup
    content: Remove unused tab module imports or use them
    status: completed
  - id: phase5-sidebar
    content: Fix sidebar collapse and Material Icons
    status: completed
  - id: phase6-test
    content: Test 10+ tickers end-to-end
    status: completed
---

# Full Metal Audit - Complete System Reset

## Executive Summary

After 12 hours of fragmented fixes, the codebase is in a chaotic state with:

- 600+ lines of dead code
- 4 duplicate flip card implementations
- Tab modules imported but not used
- Missing backend calculations
- Format mismatches between data sources
- Caching hiding fix results

---

## CRITICAL ISSUES FOUND

### Issue 1: DEAD CODE (600+ lines)

**Location:** [usa_app.py](usa_app.py) lines 590-1194

**Function:** `render_model_tab_EXAMPLE()` - NEVER CALLED

**Contains:**

- Insider Transactions tab (lines 668-750)
- Institutional Ownership tab (lines 751-830)
- Earnings Revisions tab (lines 832-954)
- DCF sub-tabs
- Analyst tab

**Impact:** Users see empty/missing features that were "implemented"

---

### Issue 2: TAB MODULES IMPORTED BUT NOT USED

**Imports in usa_app.py (lines 169-173):**

```python
from tabs.tab_data import render_data_tab
from tabs.tab_valuation import render_valuation_tab
from tabs.tab_risk import render_risk_tab
from tabs.tab_market import render_market_tab
from tabs.tab_news import render_news_tab
```

**Actual usage:** NONE - usa_app.py still has 2000+ lines of inline tab code

**Files that exist but are orphaned:**

- `tabs/tab_data.py`
- `tabs/tab_valuation.py`
- `tabs/tab_risk.py`
- `tabs/tab_market.py`
- `tabs/tab_news.py`

---

### Issue 3: 4 DUPLICATE FLIP CARD FILES

| File | Lines | Used By |

|------|-------|---------|

| `flip_cards.py` | 688 | usa_app.py, dashboard_tab.py (primary) |

| `flip_card_component.py` | 483 | analysis_tab_metrics.py, data_tab_metrics.py |

| `flip_card_v2.py` | 420 | dashboard_tab.py (fallback) |

| `flip_card_integration.py` | 600+ | test files only |

**Impact:** Inconsistent styling, duplicate code, maintenance nightmare

---

### Issue 4: MISSING BACKEND CALCULATIONS

**In `calculate_growth_rates()` [usa_backend.py](usa_backend.py) line 1871:**

Only calculates CAGR for income statement:

- Total_Revenue
- COGS
- Gross_Profit
- SGA_Expenses
- Total_Operating_Expenses
- Operating_Profit
- Net_Income

**MISSING (causes N/A):**

- Total_Assets (balance sheet)
- Total_Equity (balance sheet)
- EPS (per-share data)

**Additionally:** `calculate_growth_rates()` only called during yfinance extraction (line 1003), NOT SEC extraction

---

### Issue 5: DATA FORMAT MISMATCH

**SEC Extraction returns:**

- `Current_Assets` (underscore)
- `Total_Equity` (underscore)
- `Operating_Income` (underscore)

**yfinance returns:**

- `Current Assets` (space)
- `Stockholders Equity` (different name)
- `Operating Income` (space)

**Analysis modules expect:** yfinance format only

**Partial fix applied:** [balance_sheet_health.py](balance_sheet_health.py) now handles both, but other modules may not

---

### Issue 6: CACHE HIDES FIXES

**Cache setting in usa_app.py line 105:**

```python
@st.cache_data(ttl=3600, show_spinner=False)  # 1 HOUR cache
```

**Impact:** Any backend fix is invisible until cache expires or is manually cleared

---

### Issue 7: SIDEBAR COLLAPSE BROKEN

**Symptoms:**

- Sidebar doesn't auto-collapse
- Collapse button shows text "keyboard_arrow_indicator" instead of icon
- Material Icons CSS may not be loading

**Attempted fixes:** Multiple CSS changes in app_css.py - none fully working

---

### Issue 8: SLOW EXTRACTION (20-30 sec)

**Causes:**

- SEC API call (5-10 sec)
- yfinance fallback (5-10 sec)
- Validation layer
- Quant analysis (Fama-French)
- Multiple redundant API calls in analysis modules

---

## RECOMMENDED FIX ORDER

### Phase 1: Stabilize Backend (2-3 hours)

1. Add Total_Assets and EPS to `calculate_growth_rates()`
2. Call `calculate_growth_rates()` for SEC extraction too
3. Add index normalization helper for SEC DataFrames
4. Reduce cache TTL to 300 seconds (5 min) during testing

### Phase 2: Wire Dead Code (1-2 hours)

1. Extract Insider Transactions from dead function, wire to Risk tab
2. Extract Institutional Ownership, wire to Risk tab
3. Extract Earnings Revisions, wire to Valuation tab
4. DELETE `render_model_tab_EXAMPLE()` function

### Phase 3: Consolidate Flip Cards (1 hour)

1. Audit all 4 files, identify canonical version
2. Update all imports to use single file
3. DELETE duplicate files

### Phase 4: Clean Up Tab Imports (30 min)

1. Either USE the tab modules OR delete them
2. Remove unused imports from usa_app.py

### Phase 5: Fix UI Issues (1 hour)

1. Fix sidebar collapse CSS
2. Fix Material Icons loading
3. Test on multiple browsers

### Phase 6: Test Everything (2 hours)

1. Clear cache
2. Test 5+ tickers (AAPL, MSFT, JPM, TSLA, META)
3. Verify all tabs render
4. Verify no N/A for available data
5. Document any remaining issues

---

## FILES TO DELETE AFTER CLEANUP

| File | Reason |

|------|--------|

| `flip_card_v2.py` | Duplicate |

| `flip_card_integration.py` | Duplicate |

| `usa_app_router.py` | Failed rewrite attempt |

| `usa_app_backup.py` | Outdated backup |

| 50+ `.md` status files | Noise |

---

## SUCCESS CRITERIA

| Metric | Target |

|--------|--------|

| Dead code removed | 100% |

| Duplicate flip card files | 1 remaining |

| Asset CAGR shows value | Yes |

| EPS CAGR shows value | Yes |

| Deep Dive tabs work | All 7 |

| Insider/Ownership tabs | Visible and working |

| Sidebar collapse | Working |

| Extraction time | Under 15 seconds |

---

## ESTIMATED TIME

| Phase | Time |

|-------|------|

| Phase 1: Backend | 2-3 hours |

| Phase 2: Wire dead code | 1-2 hours |

| Phase 3: Flip cards | 1 hour |

| Phase 4: Tab imports | 30 min |

| Phase 5: UI fixes | 1 hour |

| Phase 6: Testing | 2 hours |

| **TOTAL** | **8-10 hours** |