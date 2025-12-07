# INBOX: EXECUTOR

<!-- 
DATA FILE: Tasks assigned to Executor.
For protocols and task templates, see: OPERATION_ROOM_GUIDE.txt
-->

---

## ⚠️ PARALLEL MILESTONES MODE

```
╔════════════════════════════════════════════════════════════════════════════╗
║  YOU OWN MILESTONE-007 COMPLETELY                                          ║
║                                                                            ║
║  - You design, implement, and test the entire feature                      ║
║  - No waiting for Architect                                                ║
║  - Full ownership of Performance Optimization                              ║
║  - Report completion when done                                             ║
║                                                                            ║
║  Architect is working on MILESTONE-008 (Flip Cards) in parallel.           ║
║  We sync when both are done → Heavy Testing Phase.                         ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## CURRENT ASSIGNMENT: MILESTONE-014 - Draggable Dashboard

M011 & M013 research COMPLETE ✅. Now implementing next feature.

---

### OBJECTIVE

Create a customizable dashboard where users can:
- Drag & drop metric cards to rearrange
- Save their preferred layout
- Reset to default

### WHY THIS MATTERS
- Personalization = User retention
- Professional feel = Worth paying for
- Differentiator from competitors

---

### DELIVERABLES

**1. Create `components/draggable_grid.py`:**

Use `streamlit-sortables` or custom HTML/JS implementation.

```python
# Research: streamlit-sortables package
# pip install streamlit-sortables

from streamlit_sortables import sort_items

def render_draggable_dashboard(metrics: list) -> list:
    """
    Render metrics in a draggable grid.
    Returns new order after user drags.
    """
    sorted_items = sort_items(metrics, direction="horizontal")
    return sorted_items
```

**2. Persist Layout in Session State:**

```python
if 'dashboard_layout' not in st.session_state:
    st.session_state.dashboard_layout = DEFAULT_LAYOUT

# Save after drag
st.session_state.dashboard_layout = new_order
```

**3. Add Reset Button:**

```python
if st.button("Reset Layout"):
    st.session_state.dashboard_layout = DEFAULT_LAYOUT
    st.rerun()
```

---

### FILES TO CREATE/MODIFY

| File | Action |
|------|--------|
| `components/draggable_grid.py` | CREATE - Main component |
| `dashboard_tab.py` | MODIFY - Integrate draggable |
| `requirements.txt` | ADD - streamlit-sortables |

---

### EXECUTION STEPS

1. Research `streamlit-sortables` or alternatives (5 min)
2. Create `components/draggable_grid.py` (20 min)
3. Integrate into `dashboard_tab.py` (15 min)
4. Test with 3 tickers (10 min)
5. Post completion in LIVE_CHAT

---

### SUCCESS CRITERIA

- [ ] Metrics can be dragged to new positions
- [ ] Layout persists during session
- [ ] Reset button works
- [ ] No performance degradation
- [ ] Works on all tested tickers

---

### REPORT FORMAT

```
[EXECUTOR]: M014 Complete ✅
- Created components/draggable_grid.py
- Integrated into dashboard_tab.py
- Package used: [streamlit-sortables / custom]
- Tested: AAPL, JPM, NVDA
```

---

Architect working on M015 (Mobile Responsiveness) in parallel.

---

## COMPLETED: MILESTONE-007 - Performance Optimization ✅

| Field | Value |
|-------|-------|
| **Phase** | 3 - Professional Polish |
| **Owner** | EXECUTOR (Full Ownership) |
| **Est. Time** | 4-6 hours |
| **Priority** | P0 - ✅ COMPLETED |
| **Why** | Slow = churn, fast = professional |
| **Completed** | 2025-12-08 03:50 |

---

### OBJECTIVE

Make the ATLAS engine load faster and feel snappier. Profile bottlenecks and implement optimizations.

---

### DELIVERABLES

1. **Performance Profiling Report**
   - Create `validation/performance_profile.md`
   - Time each major operation (data extraction, chart rendering, tab switching)
   - Identify top 5 bottlenecks

2. **Caching Strategy Implementation**
   - Add `@st.cache_data` to expensive API calls
   - Add `@st.cache_resource` for singleton objects
   - Ensure cache keys are correct (avoid stale data)

3. **API Call Optimization**
   - Reduce redundant yfinance calls
   - Batch requests where possible
   - Add request deduplication

4. **Lazy Loading**
   - Defer loading of non-visible tabs
   - Load charts only when expanded
   - Implement progressive loading for large datasets

5. **Streamlit Fragments (if applicable)**
   - Research `st.fragment` for partial reruns
   - Implement for independent UI sections

---

### IMPLEMENTATION GUIDE

#### Step 1: Profile Current Performance

```python
# Create profiling script: validation/profile_app.py

import time
import yfinance as yf

def profile_ticker_extraction(ticker: str):
    """Profile time taken for each data extraction step."""
    results = {}
    
    start = time.time()
    stock = yf.Ticker(ticker)
    results['yf_init'] = time.time() - start
    
    start = time.time()
    info = stock.info
    results['info_fetch'] = time.time() - start
    
    start = time.time()
    financials = stock.financials
    results['financials_fetch'] = time.time() - start
    
    start = time.time()
    balance_sheet = stock.balance_sheet
    results['balance_sheet_fetch'] = time.time() - start
    
    start = time.time()
    cash_flow = stock.cashflow
    results['cashflow_fetch'] = time.time() - start
    
    return results

# Run for test tickers
for ticker in ['AAPL', 'MSFT', 'GOOGL']:
    print(f"\n{ticker}:")
    results = profile_ticker_extraction(ticker)
    for op, duration in results.items():
        print(f"  {op}: {duration:.2f}s")
```

#### Step 2: Add Caching to usa_backend.py

```python
# Find expensive operations and add caching

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_stock_info(ticker: str) -> dict:
    """Cached stock info fetch."""
    stock = yf.Ticker(ticker)
    return stock.info

@st.cache_data(ttl=3600)
def get_stock_financials(ticker: str) -> pd.DataFrame:
    """Cached financials fetch."""
    stock = yf.Ticker(ticker)
    return stock.financials
```

#### Step 3: Optimize Redundant Calls

Look for patterns like:
```python
# BAD: Multiple yf.Ticker() calls for same ticker
stock1 = yf.Ticker(ticker)
info = stock1.info
# ... later ...
stock2 = yf.Ticker(ticker)  # REDUNDANT!
financials = stock2.financials
```

Fix by:
```python
# GOOD: Single Ticker object, cached
@st.cache_resource
def get_ticker_object(ticker: str):
    return yf.Ticker(ticker)

stock = get_ticker_object(ticker)
info = stock.info
financials = stock.financials
```

#### Step 4: Lazy Load Charts

```python
# Instead of rendering all charts on page load:
with st.expander("View Detailed Chart", expanded=False):
    # Chart only renders when user expands
    if st.session_state.get(f'{ticker}_chart_expanded'):
        render_expensive_chart(data)
```

---

### FILES TO MODIFY

| File | Change |
|------|--------|
| `usa_backend.py` | Add @st.cache_data decorators |
| `usa_app.py` | Optimize Ticker object creation |
| `dcf_modeling.py` | Cache DCF calculations |
| `earnings_revisions.py` | Already has caching, verify |
| `insider_transactions.py` | Add caching if missing |
| `institutional_ownership.py` | Add caching if missing |

### FILES TO CREATE

| File | Purpose |
|------|---------|
| `validation/performance_profile.md` | Profiling results |
| `validation/profile_app.py` | Profiling script |

---

### TESTING CHECKLIST

- [ ] Profile AAPL extraction time (before/after)
- [ ] Profile MSFT extraction time (before/after)
- [ ] Profile tab switching speed
- [ ] Verify cached data is fresh (not stale)
- [ ] Test cache invalidation works
- [ ] No new errors introduced

---

### SUCCESS METRICS

| Metric | Current (est.) | Target |
|--------|---------------|--------|
| Initial load time | ~8-10s | < 5s |
| Tab switch time | ~2-3s | < 1s |
| Repeat ticker load | ~8-10s | < 2s (cached) |

---

### REPORTING

When complete, post in `LIVE_CHAT.md`:

```
[EXECUTOR]: [DONE] MILESTONE-007 Complete.
- Profiled app: [list bottlenecks found]
- Added caching to: [list files]
- Performance improvement: X% faster initial load
- Repeat loads: X% faster (cached)
- Created validation/performance_profile.md
```

---

### NOTES

- **DON'T** break existing functionality for speed
- **DON'T** cache data that should be fresh (real-time prices)
- **DO** use appropriate TTL values (1 hour for fundamentals, shorter for prices)
- **DO** test thoroughly - caching bugs are hard to debug

---

## COMPLETED MILESTONES

| Milestone | Status | Notes |
|-----------|--------|-------|
| MILESTONE-006 (White-Label) | ✅ DONE | 5 themes, CSS injection |

---

<!-- 
END OF INBOX
For protocols: see OPERATION_ROOM_GUIDE.txt
-->
