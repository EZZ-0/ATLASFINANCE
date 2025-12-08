# ATLAS MAJOR FIX PLAN
## Post-Manual-Testing Comprehensive Audit & Fix Strategy
**Date:** December 8, 2024  
**Status:** CRITICAL - Maintenance Mode ENABLED

---

## MANUAL TEST RESULTS ANALYSIS

### OVERALL SCORE: ~35% PASS RATE (Estimated 22/63 tests)

| Section | Passed | Failed | Pass Rate |
|---------|--------|--------|-----------|
| 1. Landing Page | 4 | 2 | 67% |
| 2. Search/Extraction | 1 | 4 | 20% |
| 3. Dashboard | 1 | 4 | 20% |
| 4. Data Tab | 2 | 3 | 40% |
| 5. Deep Dive | 1 | 5 | 17% |
| 6. Valuation | 0 | 5 | 0% |
| 7. Risk/Ownership | 2 | 3 | 40% |
| 8. Market Intel | 2 | 3 | 40% |
| 9. News | 2 | 1 | 67% |
| 10. IC Memo | 1 | 3 | 25% |
| 11. UI/UX | 2 | 3 | 40% |
| 12. Edge Cases | 2 | 2 | 50% |
| 13. Data Accuracy | 3 | 2 | 60% |

---

## CRITICAL ISSUES BY PRIORITY

### P0 - SHOWSTOPPERS (Must fix before going live)

| # | Issue | Location | User Description | Root Cause Analysis |
|---|-------|----------|------------------|---------------------|
| 1 | **Theme One-Click-Behind** | `app_themes.py` | First click changes partially, second click applies previous selection | Session state not updating before rerun |
| 2 | **DCF Redirects to Dashboard** | `usa_app.py` | Running DCF sends user back to dashboard | `st.rerun()` or tab switching logic error |
| 3 | **62.5% N/A Rate in Deep Dive** | `analysis_tab.py` + modules | 10/16 flip cards show N/A | Field mapper not finding values OR analysis modules not receiving data |
| 4 | **Flip Cards Out of Frame** | `flip_cards.py` + CSS | Click to flip causes card to go out of frame | CSS positioning issue |
| 5 | **Monte Carlo Not Integrated** | `usa_app.py` | No Monte Carlo simulation anywhere | Dead code - never wired |
| 6 | **Quant Tab Fully Deleted** | `tabs/tab_market.py` | Quant analysis section gone | Import or render missing |
| 7 | **Institutional Ownership 0%** | `institutional_ownership.py` | Top 10 Concentration shows 0.0% | Data extraction or calculation issue |
| 8 | **Peer Discovery 0 Peers** | `compare_tab.py` | Auto-discover returns 0 peers | API or logic issue |

### P1 - HIGH PRIORITY

| # | Issue | Location | User Description | Root Cause Analysis |
|---|-------|----------|------------------|---------------------|
| 9 | **No Price Chart on Dashboard** | `dashboard_tab.py` | "What price chart?? No chart" | Chart not rendered or hidden |
| 10 | **Sidebar Text Overflow** | `app_css.py` | Text broken while collapsed showing partial text | CSS width/overflow issue |
| 11 | **Flip Cards No Hover Effect** | `flip_cards.py` | No hover, click only, but broken animation | CSS transform not working |
| 12 | **Cash Flow Table Empty** | Data tab in `usa_app.py` | Only date column, no row items | DataFrame rendering issue |
| 13 | **Earnings Revisions Error** | `earnings_revisions.py` | Error: 'current_estimate' | KeyError in data extraction |
| 14 | **Insider Activity Same Numbers** | `insider_transactions.py` | Always shows Total: 20, Buys: 0, Sells: 0 | Hardcoded or cached data |
| 15 | **UI Breaks on Rapid Navigation** | Risk tab | Half screen issue on scroll up/down | CSS or state management |

### P2 - MEDIUM PRIORITY

| # | Issue | Location | User Description |
|---|-------|----------|------------------|
| 16 | **Extraction Time 18-25 secs** | `usa_backend.py` | All tickers taking 18-19+ seconds | Need caching or parallel fetching |
| 17 | **No Sector-Specific Metrics** | Various | No bank-specific, retail-specific metrics | Feature not implemented |
| 18 | **Icon Inconsistency** | `app_css.py` | Different arrows for sidebar, emojis everywhere | Need consistent icon system |
| 19 | **IC Memo Dropdown Issues** | `investment_summary.py` | Full description in dropdown, shows in PDF | Improper use of expander |
| 20 | **PDF Alpha Signals N/A** | PDF export | Alpha Signals show N/A in exported PDF | Data not passed to PDF |
| 21 | **News Links Not on Headlines** | News tab | Links work but not on headline | HTML structure |
| 22 | **Peer Comparison Slow (15 secs)** | `compare_tab.py` | Adding peer takes too long | No caching |
| 23 | **No Recommendations Section** | `investment_summary.py` | No dedicated recommendations | Missing feature |

### P3 - LOW PRIORITY / ENHANCEMENTS

| # | Issue | User Request |
|---|-------|--------------|
| 24 | **TTM Data Option** | "Need option to switch to TTM for users" |
| 25 | **Better Fonts** | "Needs better professional/special fonting" |
| 26 | **Professional Themes** | "Themes are basic, ugly, unprofessional" |
| 27 | **Charts/Dropdowns in Risk Tab** | "Chart and table are dropdowns, shouldn't be" |
| 28 | **Site Reloading on Button Click** | "Stop site from reloading on every button click" |

---

## PREVIOUS SOLUTIONS THAT FAILED

| Attempt | What We Tried | Why It Failed | Correct Approach |
|---------|---------------|---------------|------------------|
| Router Rewrite | Created `usa_app_router.py` | Lost features, broke sidebar, introduced new bugs | Incremental fixes to `usa_app.py` |
| Fuzzy Field Matching | Added fuzzy matching to `field_mapper.py` | Performance issues, false positives | Pre-computed lookup tables (O(1)) |
| Flip Card V2/V3 | Created multiple flip card files | Inconsistent usage, duplicated code | Single `flip_cards.py` with proper CSS |
| CSS Icon Fix | Added Material Symbols font | Font not loading correctly | Need fallback Unicode icons |
| Analysis Module Data Pass | Passed `financials` dict to modules | Some modules still calling yfinance directly | Must audit ALL modules |
| SEC Format Handling | Added `_normalize_dataframe_index()` | Some fields still using underscore format | Need universal normalization |

---

## PHASED FIX PLAN

### PHASE 0: Pre-Work (30 min) ✅ COMPLETE
- [x] Enable maintenance mode on deployed site
- [x] Create backup branch (`pre-major-fix-backup`)
- [x] Verify all previous commits saved

### COMPLETED FIXES (as of this session):

| # | Issue | Status | Notes |
|---|-------|--------|-------|
| 1 | Theme one-click-behind | ✅ FIXED | Added `st.rerun()` on theme change |
| 2 | Sidebar text overflow | ✅ FIXED | Added CSS overflow handling |
| 3 | DCF redirects to dashboard | ✅ FIXED | Removed unnecessary `st.rerun()` |
| 4 | Flip cards out of frame | ✅ FIXED | Improved CSS positioning, added hover |
| 5 | Quant tab deleted | ✅ FIXED | Always show tab, handle missing data |
| 6 | Earnings revisions error | ✅ FIXED | Fixed incorrect dict key access |
| 7 | Cash flow table empty | ✅ FIXED | Expanded XBRL tag search |
| 8 | Institutional ownership 0% | ✅ FIXED | Fixed % column name variations |
| 9 | Peer discovery 0 peers | ✅ FIXED | Added sector name normalization |

---

## DETAILED ROOT CAUSE ANALYSIS (Dec 8 Investigation)

### ISSUE 1: FLIP CARDS BROKEN EVERYWHERE (Except Dashboard)

**Root Cause:** TWO different implementations exist:

| Location | Implementation | Status |
|----------|----------------|--------|
| `flip_cards.py` | CSS animation via `components.html()` | ✅ Works (Dashboard only) |
| `analysis_tab_metrics.py` line 336 | `st.button("↻")` + `st.rerun()` | ❌ Clunky, server round-trip |
| `data_tab_metrics.py` line 444 | `st.button("↻")` + `st.rerun()` | ❌ Clunky, server round-trip |

**Design Issues in flip_cards.py:**
- Font sizes: 0.55-0.72rem (too small, unreadable)
- Card height: 100px (too cramped for content)
- No professional font family
- Line clamp: 3 (cuts off educational content)

**Files to modify:** `flip_cards.py`, `analysis_tab_metrics.py`, `data_tab_metrics.py`

---

### ISSUE 2: DEEP DIVE N/A RATE (62.5%)

**Root Cause:** Analysis modules use yfinance which has inconsistent data. FMP API provides more reliable data.

**Evidence:** `analysis_tab_metrics.py` uses hardcoded keys like `metrics.get('earnings_score')` - if analysis module returns different keys, shows N/A.

**Solution:** Use FMP API (`fmp_extractor.py`) as primary data source - already exists but not wired.

**Files to modify:** `valuation_multiples.py`, `balance_sheet_health.py`, `management_effectiveness.py`, `cashflow_analysis.py`

---

### ISSUE 3: MISSING PRICE CHART (Dashboard)

**Root Cause:** `visualization.py` has 11 plot functions but NO stock price chart:
- `plot_revenue_trend`, `plot_margin_analysis`, `plot_dcf_comparison`, etc.
- Missing: `plot_stock_price()` or `plot_historical_prices()`

**Files to modify:** `visualization.py` (add function), `dashboard_tab.py` (call it)

---

### ISSUE 4: MONTE CARLO NOT INTEGRATED

**Root Cause:** Complete code exists as DEAD CODE:
- `monte_carlo_engine.py` - 645 lines, full simulation engine
- `monte_carlo_ui.py` - 471 lines, complete Streamlit UI
- `usa_app.py` NEVER imports or calls these

**Files to modify:** `usa_app.py` Valuation tab (import and render `monte_carlo_ui.render_monte_carlo_button()`)

---

### ISSUE 5: IC MEMO DROPDOWN ISSUES

**Root Cause:** `investment_summary.py` lines 936-951 use expander for long business descriptions. Shows truncated text (400 chars) with "Show More" expander.

**User wants:** Full text visible by default, hidden when exporting to PDF

**Files to modify:** `investment_summary.py`

---

## REVISED PHASED FIX PLAN

### PHASE 1: FLIP CARDS OVERHAUL (HIGH PRIORITY) - 4 hours

#### Step 1A: Fix Design in `flip_cards.py` (1 hour)

| Property | Current | Target | Reason |
|----------|---------|--------|--------|
| Card height | 100px | 140px | More room for content |
| Label font | 0.72rem | 0.85rem | Readable |
| Value font | 1.35rem | 1.7rem | Prominent |
| Formula font | 0.68rem | 0.9rem | Legible |
| Insight font | 0.68rem | 0.85rem | Educational content readable |
| Benchmark font | 0.58rem | 0.75rem | Visible |
| Line clamp | 3 | 5 | Show full insight |
| Font family | System | Plus Jakarta Sans | Professional |
| Animation | 0.6s | 0.45s | Snappier feel |
| Padding | 12px | 16px | Less cramped |

#### Step 1B: Propagate to All Tabs (2 hours)

| Task | File | Action |
|------|------|--------|
| 1B.1 | `analysis_tab_metrics.py` | Remove OLD `_render_analysis_flip()`, import from `flip_cards.py` |
| 1B.2 | `data_tab_metrics.py` | Remove OLD `_render_simple_flip()`, import from `flip_cards.py` |
| 1B.3 | Delete old files | Remove `flip_card_component.py`, `flip_card_v2.py`, `flip_card_integration.py` |

#### Step 1C: Test (1 hour)
- Dashboard flip cards
- Data tab flip cards  
- Deep Dive flip cards
- Verify no `st.rerun()` calls remain in flip logic

---

### PHASE 2: FMP INTEGRATION FOR N/A REDUCTION (HIGH PRIORITY) - 2 hours

**Why:** 62.5% N/A rate unacceptable. FMP provides reliable, standardized data.
**Prerequisite:** `FMP_API_KEY` in `.env` file

| Task | File | Action |
|------|------|--------|
| 2.1 | Verify FMP key | Check `.env` has `FMP_API_KEY` |
| 2.2 | `valuation_multiples.py` | Use `FMPExtractor` for P/E, P/B, EV/EBITDA |
| 2.3 | `balance_sheet_health.py` | Use FMP for current ratio, D/E |
| 2.4 | `management_effectiveness.py` | Use FMP for ROE, ROA, ROIC |
| 2.5 | `cashflow_analysis.py` | Use FMP for FCF, OCF metrics |
| 2.6 | Test | Verify N/A rate drops to <15% |

**FMP Provides:**
- `peRatioTTM`, `returnOnEquityTTM`, `returnOnAssetsTTM`
- `currentRatioTTM`, `debtEquityRatioTTM`, `dividendYieldTTM`
- Historical prices for charts

---

### PHASE 3: MISSING FEATURES (MEDIUM PRIORITY) - 3 hours

| Task | File | Action |
|------|------|--------|
| 3.1 | `visualization.py` | Add `plot_stock_price()` function |
| 3.2 | `dashboard_tab.py` | Call price chart function |
| 3.3 | `usa_app.py` | Import `monte_carlo_ui`, add to Valuation tab |
| 3.4 | `investment_summary.py` | Fix business description (no dropdown, full text) |
| 3.5 | `investment_summary.py` | Add recommendations section |

---

### PHASE 4: IC MEMO & PDF (LOW PRIORITY) - 1 hour

| Task | File | Action |
|------|------|--------|
| 4.1 | `investment_summary.py` | Show full business description by default |
| 4.2 | `investment_summary.py` | Add dedicated recommendations section |
| 4.3 | PDF export | Fix Alpha Signals N/A |

---

### PHASE 5: POLISH (LOW PRIORITY) - 1 hour

| Task | File | Action |
|------|------|--------|
| 5.1 | `app_themes.py` | Improve 3 theme color palettes |
| 5.2 | `app_css.py` | Better font stack (Plus Jakarta Sans) |
| 5.3 | News tab | Make headlines clickable |

---

### PHASE 6: TESTING & LAUNCH - 1 hour

- [ ] Test all 63 scenarios from manual checklist
- [ ] Verify 90%+ pass rate
- [ ] Verify N/A rate <15%
- [ ] Set `MAINTENANCE_MODE = False` in `usa_app.py`
- [ ] Deploy

---

## ESTIMATED TIMELINE

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 0: Pre-Work | 30 min | 30 min |
| Phase 1: Core Data | 2-3 hours | 3.5 hours |
| Phase 2: UI/UX | 2 hours | 5.5 hours |
| Phase 3: Features | 2-3 hours | 8.5 hours |
| Phase 4: IC Memo | 1 hour | 9.5 hours |
| Phase 5: Performance | 1 hour | 10.5 hours |
| Phase 6: Polish | 1 hour | 11.5 hours |
| Phase 7: Testing | 1 hour | 12.5 hours |
| **TOTAL** | **12-14 hours** | |

---

## SUCCESS CRITERIA

| Metric | Current | Target |
|--------|---------|--------|
| Overall Pass Rate | ~35% | >90% |
| N/A Rate (Deep Dive) | 62.5% | <15% |
| Extraction Time | 18-25s | <10s |
| Theme Application | 2 clicks | 1 click |
| Flip Cards Working | No | Yes |
| Monte Carlo | Missing | Working |
| Quant Tab | Deleted | Restored |
| Price Chart | Missing | Visible |

---

## QUICK WINS (Can do in <15 min each)

1. **Theme fix** - Add `st.rerun()` after theme change
2. **Sidebar overflow** - Add `overflow: hidden` CSS
3. **Icon fallback** - Use Unicode arrows ◀ ▶
4. **Earnings error** - Add try/except for 'current_estimate'
5. **Restore Quant** - Uncomment or re-import in tab_market.py

---

## FILES TO AUDIT

Priority order for code review:

1. `usa_app.py` - Main app, DCF redirect issue
2. `analysis_tab.py` - Deep dive N/A issues
3. `flip_cards.py` - Animation/hover issues
4. `app_themes.py` - Theme one-click-behind
5. `tabs/tab_market.py` - Missing Quant
6. `tabs/tab_valuation.py` - Monte Carlo integration
7. `dashboard_tab.py` - Missing price chart
8. `institutional_ownership.py` - 0% ownership
9. `compare_tab.py` - Peer discovery
10. `earnings_revisions.py` - current_estimate error

---

## NOTES

- **DO NOT** attempt another full router rewrite
- **DO** incremental fixes with testing after each
- **DO** commit after each phase
- **DO** verify fix before moving to next issue
- Backup before any major change

---

## MAINTENANCE MODE

Currently ENABLED in `usa_app.py`:
```python
MAINTENANCE_MODE = True  # Line ~15
```

To go live again:
```python
MAINTENANCE_MODE = False
```

---

*Created by AI Assistant after comprehensive manual test analysis*

