# ATLAS Testing Checkpoint
## Manual Testing Checklist - All Milestones

**Generated:** 2025-12-08  
**Version:** Post M016 (Auth Complete)  
**Monetization Flag:** OFF (Free access for testers)

---

## How to Test

1. Run the app: `streamlit run usa_app.py`
2. Open browser to `http://localhost:8501`
3. Follow checklist below - each test has detailed steps
4. Mark items ✅ or ❌
5. Note any bugs in the Issues section at bottom

---

## PHASE 1: Data Foundation (M001)

### WACC & DCF Calculations

| #   | Test             | Status |
|-----|------------------|--------|
| 1.1 | WACC displays    | ⬜     |
| 1.2 | Beta is adjusted | ⬜     |
| 1.3 | Risk-free rate   | ⬜     |
| 1.4 | FCF methods      | ⬜     | all fail no model tab

**Test 1.1: WACC Displays**
1. Search "AAPL" in the ticker search box
2. Wait for data to load (5-15 seconds)
3. Click the **"Model"** main tab (tab 2) we dont have a fucking tab called model, if you make such a simple mistake how can i trust u?
4. Click the **"DCF"** sub-tab (first sub-tab)
5. Scroll down to find "Discount Rate (WACC)"
6. **PASS:** WACC value shows (e.g., "9.2%")
7. **FAIL:** Shows "N/A" or no WACC metric visible

**Test 1.2: Beta is Adjusted**
1. Same DCF tab as 1.1
2. Look for any beta display (may be in tooltips or details)
3. If shown, check if it says "Adjusted Beta" not just "Beta"
4. **Alternative:** Check terminal output when running app - look for "Beta adjustment: X.XXX → X.XXX"
5. **PASS:** Shows adjusted beta value or terminal confirms adjustment
6. **FAIL:** Only shows raw beta, no adjustment visible

**Test 1.3: Risk-Free Rate**
1. Same DCF tab as 1.1
2. The WACC should use a risk-free rate around 4-4.5%
3. This is embedded in the WACC calculation
4. **PASS:** WACC value is reasonable (7-12% for most stocks)
5. **FAIL:** WACC is 0%, negative, or extremely high (>20%)

**Test 1.4: FCF Methods**
1. In DCF tab, look for a dropdown labeled "FCF Method" or "Cash Flow Method"
2. Click the dropdown
3. **PASS:** Shows 4 options (Simple, Levered, Owner Earnings, FCFF)
4. **FAIL:** No dropdown, or only 1 option, or dropdown doesn't work

### Industry Benchmarks

| #   | Test            | Status |
|-----|-----------------|--------|
| 1.5 | Sector shown    | ⬜     |
| 1.6 | Benchmarks work | ⬜     | all fail nothing exist or implemented

**Test 1.5: Sector Shown**
1. Search "AAPL"
2. Click **"Data"** main tab (tab 1)
3. Look at company info section at the top
4. **PASS:** Shows sector like "Technology" or "Consumer Electronics"
5. **FAIL:** No sector shown anywhere

**Test 1.6: Benchmarks Work**
1. Search "AAPL"
2. Click **"Deep Dive"** main tab (tab 3)
3. Click **"Valuation"** sub-tab
4. Look for industry comparison or percentile rankings
5. **PASS:** Shows comparison text like "vs sector average" or percentile
6. **FAIL:** Only shows raw metrics, no comparison

---

## PHASE 2: Alpha Signals (M002-M004)

### Earnings Revisions (M002)

| #   | Test            | Status |
|-----|-----------------|--------|
| 2.1 | Tab exists      | ⬜     |
| 2.2 | Data displays   | ⬜     |
| 2.3 | Trend indicator | ⬜     | all fails similar to why above 2

**Test 2.1: Earnings Revisions Tab Exists**
1. Search "AAPL"
2. Click **"Model"** main tab
3. Look for **"Earnings Rev"** or **"Revisions"** sub-tab
4. Click it
5. **PASS:** Tab loads without error
6. **FAIL:** Tab missing, or clicking shows error

**Test 2.2: Earnings Revisions Data**
1. In Earnings Revisions tab from 2.1
2. Look for analyst estimate data
3. **PASS:** Shows metrics like "30-day change", "90-day change", estimate numbers
4. **FAIL:** Shows "No data" or empty section

**Test 2.3: Trend Indicator**
1. In Earnings Revisions tab
2. Look for trend/momentum indicator
3. **PASS:** Shows direction (up/down/flat) or momentum score
4. **FAIL:** No trend indication visible

### Insider Transactions (M003)

| #   | Test             | Status |
|-----|------------------|--------|
| 3.1 | Tab exists       | ⬜     |
| 3.2 | Summary shown    | ⬜     |
| 3.3 | Sentiment gauge  | ⬜     |
| 3.4 | Transaction list | ⬜     | all fail same thing

**Test 3.1: Insider Tab Exists**
1. Search "AAPL"
2. Click **"Model"** main tab
3. Look for **"Insider"** sub-tab
4. Click it
5. **PASS:** Tab loads without error
6. **FAIL:** Tab missing or crashes

**Test 3.2: Insider Summary**
1. In Insider tab from 3.1
2. Look at the top metrics section
3. **PASS:** Shows metrics like "Total Buys", "Total Sells", "Net Value"
4. **FAIL:** No summary metrics visible

**Test 3.3: Sentiment Gauge**
1. In Insider tab
2. Look for a gauge chart or sentiment indicator
3. **PASS:** Shows a gauge labeled "Bullish/Bearish" or similar visual
4. **FAIL:** No gauge, just text only

**Test 3.4: Transaction List**
1. In Insider tab
2. Scroll down or look for expandable section
3. **PASS:** Shows table of recent insider trades with dates, names, amounts
4. **FAIL:** No transaction details visible

### Institutional Ownership (M004)

| #   | Test                | Status |
|-----|---------------------|--------|
| 4.1 | Tab exists          | ⬜     |
| 4.2 | Percentages shown   | ⬜     |
| 4.3 | Top holders         | ⬜     |
| 4.4 | Accumulation signal | ⬜     | all fail same reason

**Test 4.1: Ownership Tab Exists**
1. Search "AAPL"
2. Click **"Model"** main tab
3. Look for **"Ownership"** sub-tab
4. Click it
5. **PASS:** Tab loads without error
6. **FAIL:** Tab missing or crashes

**Test 4.2: Ownership Percentages**
1. In Ownership tab from 4.1
2. Look at top metrics
3. **PASS:** Shows "Institutional %" and "Insider %" (e.g., "78.5%", "0.07%")
4. **FAIL:** Percentages show 0% or N/A for major stock like AAPL

**Test 4.3: Top Holders List**
1. In Ownership tab
2. Look for table of top institutional holders
3. **PASS:** Shows top 5-10 holders (Vanguard, BlackRock, etc.) with share counts
4. **FAIL:** No holder list visible

**Test 4.4: Accumulation Signal**
1. In Ownership tab
2. Look for "Accumulating"/"Distributing" indicator
3. **PASS:** Shows signal text or score indicating smart money direction
4. **FAIL:** No accumulation signal visible

---

## PHASE 3: Professional Polish (M005-M008)

### PDF Export (M005)

| #   | Test            | Status |
|-----|-----------------|--------|
| 5.1 | Export button   | ⬜     |
| 5.2 | PDF generates   | ⬜     |
| 5.3 | PDF readable    | ⬜     |
| 5.4 | Enhanced option | ⬜     | all fail no summary tab

**Test 5.1: PDF Export Button Exists**
1. Search "AAPL"
2. Click **"Summary"** main tab (last tab)
3. Scroll to bottom of the page
4. **PASS:** See "Download PDF" or "Export Report" button
5. **FAIL:** No export button visible

**Test 5.2: PDF Generates**
1. Click the PDF export button from 5.1
2. Wait a few seconds
3. **PASS:** Browser shows download prompt or download starts
4. **FAIL:** Nothing happens, or error message appears

**Test 5.3: PDF Content is Readable**
1. Open the downloaded PDF file
2. Review content
3. **PASS:** Text is formatted, tables are aligned, no garbled text
4. **FAIL:** PDF is blank, text is jumbled, or images missing

**Test 5.4: Enhanced PDF Option**
1. On Summary tab, look for PDF type selector
2. Select "Enhanced IC Memo" option
3. Click download
4. **PASS:** Different/enhanced PDF format downloads
5. **FAIL:** No option selector, or same PDF as standard

### White-Label Themes (M006)

| #   | Test           | Status |
|-----|----------------|--------|
| 6.1 | Theme selector | ⬜     |
| 6.2 | Dark theme     | ⬜     |
| 6.3 | Light theme    | ⬜     |
| 6.4 | Theme persists | ⬜     | side bar broken non functional cant collapse has to update for this feature

**Test 6.1: Theme Selector Exists**
1. Look at the **left sidebar** (click hamburger if collapsed)
2. Scroll down in sidebar
3. **PASS:** See "Theme" dropdown with options
4. **FAIL:** No theme selector visible

**Test 6.2: Dark Theme Works**
1. In theme dropdown, select "Atlas Dark"
2. **PASS:** Background becomes dark, text light
3. **FAIL:** No visual change

**Test 6.3: Light Theme Works**
1. In theme dropdown, select "Atlas Light"
2. **PASS:** Background becomes light, text dark
3. **FAIL:** No visual change

**Test 6.4: Theme Persists**
1. Select a different theme
2. Click between different main tabs
3. **PASS:** Theme stays the same across tabs
4. **FAIL:** Theme resets when changing tabs

### Performance (M007)

| #   | Test          | Status |
|-----|---------------|--------|
| 7.1 | Initial load  | ⬜     | very bad 20 secs and longer
| 7.2 | Ticker search | ⬜     |20 secs fail
| 7.3 | Tab switching | ⬜     |clunky not smooth at all
| 7.4 | Cached reload | ⬜     | cant fully evaluate due to many failures 

**Test 7.1: Initial Load Time**
1. Close all browser tabs
2. Run `streamlit run usa_app.py`
3. Open `http://localhost:8501`
4. Start timer when you hit Enter, stop when page is interactive
5. **PASS:** Loads in < 10 seconds
6. **FAIL:** Takes > 15 seconds

**Test 7.2: Ticker Search Time**
1. Search "MSFT" (first time, not cached)
2. Time from pressing Enter to data displayed
3. **PASS:** Data loads in < 8 seconds
4. **FAIL:** Takes > 15 seconds

**Test 7.3: Tab Switching Speed**
1. With data loaded, click between tabs quickly
2. **PASS:** Each tab loads in < 2 seconds
3. **FAIL:** Tab switching freezes or takes > 5 seconds

**Test 7.4: Cached Reload**
1. Search "MSFT" again (same ticker)
2. Time the reload
3. **PASS:** Loads in < 3 seconds (cached)
4. **FAIL:** Same slow time as first load

### Flip Cards (M008)

| #   | Test           | Status |
|-----|----------------|--------|
| 8.1 | Cards visible  | ⬜     | horrible   
| 8.2 | Click to flip  | ⬜     |horrible, beside dashbnoard tab all other are clunky ugly and button flip not box flip very horrible i wasted time and money on multiple agents...
| 8.3 | Formula shown  | ⬜     |horrible layout boxes over lay, and has ivisible boarders that cuts out content, extremly horrible
| 8.4 | Insight shown  | ⬜     |text not clear, fonts horrible and size is small ,if can integrate safely and smoothly 
| 8.5 | Colors correct | ⬜     |colors and fonts quality horrible

**Test 8.1: Flip Cards Visible**
1. Search "AAPL"
2. Click **"Visualize"** main tab (tab 3) → **"Dashboard"** sub-tab
3. Look at the key metrics section at the top
4. **PASS:** See styled metric cards (not plain st.metric boxes)
5. **FAIL:** Only plain gray metric boxes

**Test 8.2: Click to Flip**
1. Click on any metric card (e.g., P/E Ratio)
2. **PASS:** Card flips with animation to show back side
3. **FAIL:** Nothing happens on click, or page refreshes

**Test 8.3: Formula Shown on Back**
1. Flip a card (from 8.2)
2. Look at the back of the card
3. **PASS:** Shows formula like "Price ÷ EPS"
4. **FAIL:** Back is blank or no formula

**Test 8.4: Insight Shown on Back**
1. Same flipped card
2. **PASS:** Shows insight text explaining what the metric means
3. **FAIL:** No insight text

**Test 8.5: Colors Match State**
1. Look at multiple flip cards
2. Check colors: Green should be good, Red should be bad
3. **PASS:** High ROE is green, High Debt/Equity is red
4. **FAIL:** Colors seem random or all same color

---

## PHASE 4: Data Quality (M011-M013)

### Ticker Handling (M011)

| #    | Test             | Status |
|------|------------------|--------|
| 11.1 | Valid ticker     | ⬜     |pass
| 11.2 | Invalid ticker   | ⬜     |pass
| 11.3 | Case insensitive | ⬜     |pass

**Test 11.1: Valid Ticker Works**
1. Search "AAPL"
2. **PASS:** Data loads, company name "Apple Inc." shown
3. **FAIL:** Error message or no data

**Test 11.2: Invalid Ticker Handled**
1. Search "XXXXX" (nonsense ticker)
2. **PASS:** Shows friendly error like "Ticker not found"
3. **FAIL:** App crashes or shows technical error

**Test 11.3: Case Insensitive**
1. Search "aapl" (lowercase)
2. **PASS:** Loads same data as "AAPL"
3. **FAIL:** Error or different result

### Bank Metrics (M012)

| #    | Test           | Status |
|------|----------------|--------|
| 12.1 | Bank detection | ⬜     | wont test until fix previous issues
| 12.2 | Bank metrics   | ⬜     |
| 12.3 | No FCF shown   | ⬜     |

**Test 12.1: Bank Ticker Loads**
1. Search "JPM" (JPMorgan Chase)
2. **PASS:** Data loads without error
3. **FAIL:** Error or crash

**Test 12.2: Bank-Specific Metrics**
1. With JPM loaded, check Dashboard metrics
2. Look for P/B (Price to Book) metric
3. **PASS:** Shows P/B prominently (banks use this instead of D/E)
4. **FAIL:** Shows Debt/Equity which is meaningless for banks

**Test 12.3: No FCF for Banks**
1. With JPM loaded, check Dashboard
2. Look for FCF (Free Cash Flow) metric
3. **PASS:** FCF is hidden or shows Dividend Yield instead
4. **FAIL:** Shows FCF (which is misleading for banks)

---

## PHASE 5: UX (M014-M015)

### Draggable Dashboard (M014)

| #    | Test            | Status |
|------|-----------------|--------|
| 14.1 | Reorder control | ⬜     | horrible clunky and not effectively working for all items in this test
| 14.2 | Presets work    | ⬜     |
| 14.3 | Reset works     | ⬜     |

**Test 14.1: Layout Controls Exist**
1. Go to Dashboard tab
2. Look for "Customize Layout" expander or similar control
3. **PASS:** Control visible to reorder metrics
4. **FAIL:** No layout customization option

**Test 14.2: Preset Layouts Work**
1. Click "Customize Layout" expander
2. Select a preset like "Valuation Focus"
3. **PASS:** Dashboard reorganizes to show different metrics
4. **FAIL:** Nothing changes

**Test 14.3: Reset Works**
1. In layout customization, click "Reset to Default"
2. **PASS:** Dashboard returns to original layout
3. **FAIL:** No reset option or doesn't work

### Mobile Responsive (M015)

| #    | Test          | Status |
|------|---------------|--------|
| 15.1 | Desktop view  | ⬜     |not tested ut side desktop already horrible on desktop responsivness imagine mobile
| 15.2 | Tablet view   | ⬜     |
| 15.3 | Mobile view   | ⬜     |
| 15.4 | Touch targets | ⬜     |

**Test 15.1: Desktop View**
1. Open app in full-width browser (1920px wide)
2. **PASS:** 4-5 column layout, no horizontal scroll needed
3. **FAIL:** Elements overlap or very narrow

**Test 15.2: Tablet View**
1. Resize browser to ~768px width (or use DevTools responsive mode)
2. **PASS:** Layout adapts to 2-3 columns
3. **FAIL:** Same layout as desktop, requires horizontal scroll

**Test 15.3: Mobile View**
1. Resize browser to ~400px width
2. **PASS:** Single column layout, everything readable
3. **FAIL:** Elements overflow, text cut off

**Test 15.4: Touch Targets**
1. In mobile view (400px)
2. Check button sizes
3. **PASS:** Buttons are at least 44px tall (tappable)
4. **FAIL:** Tiny buttons hard to tap

---

## PHASE 6: Monetization (M016)

### Auth System (Currently OFF)

| #    | Test              | Status |
|------|-------------------|--------|
| 16.1 | No login required | ⬜     |
| 16.2 | No limits         | ⬜     |
| 16.3 | All features work | ⬜     |

**Test 16.1: No Login Prompt**
1. Open app fresh (clear cookies if needed)
2. **PASS:** App loads directly to search, no login form
3. **FAIL:** Sees login/register form blocking access

**Test 16.2: No Usage Limits**
1. Search 5+ different tickers one after another
2. **PASS:** All work, no "limit reached" message
3. **FAIL:** Gets blocked after X analyses

**Test 16.3: All Features Accessible**
1. Try PDF export, Monte Carlo, all tabs
2. **PASS:** Everything works without "upgrade to Pro" blocks
3. **FAIL:** Some features locked

**Note:** Auth is behind `MONETIZATION_ENABLED=false` flag in `auth/config.py`.

---

## Cross-Functional Tests

### General App Health

| #   | Test              | Status |
|-----|-------------------|--------|
| X.1 | No console errors | ⬜     |
| X.2 | All tabs load     | ⬜     |
| X.3 | Multiple tickers  | ⬜     |
| X.4 | S&P 500 dropdown  | ⬜     |

**Test X.1: No Console Errors**
1. Open browser DevTools (F12) → Console tab
2. Use the app normally for 2 minutes
3. **PASS:** No red error messages
4. **FAIL:** Multiple red errors appearing

**Test X.2: All Tabs Load**
1. With ticker loaded, click every main tab and sub-tab
2. **PASS:** All load without crash
3. **FAIL:** Any tab shows error or blank

**Test X.3: Multiple Tickers**
1. Search: AAPL, MSFT, JPM, TSLA, KO (one at a time)
2. **PASS:** All 5 load successfully
3. **FAIL:** Any fails to load

**Test X.4: S&P 500 Dropdown**
1. Click the S&P 500 dropdown (if visible in sidebar)
2. Select a random company
3. **PASS:** Selected company loads
4. **FAIL:** Dropdown missing or selection fails

### Test Tickers (Diverse Coverage)

| Ticker | Type                 | Status |
|--------|----------------------|--------|
| AAPL   | Tech mega-cap        | ⬜     |
| JPM    | Bank                 | ⬜     |
| XOM    | Energy               | ⬜     |
| TSLA   | Growth (no dividend) | ⬜     |
| KO     | Consumer staples     | ⬜     |
| NVDA   | Semiconductor        | ⬜     |
| JNJ    | Healthcare           | ⬜     |

For each ticker: Search → Check Dashboard loads → Check DCF tab → Note any errors.

---

## Issues Found
 = check User typed in findings over all hhuge faliure 
| #   | Description | Severity | Milestone | Fixed? |
|-----|-------------|----------|-----------|--------|
|     |             |          |           |        |
|     |             |          |           |        |
|     |             |          |           |        |

**Severity Levels:**
- 🔴 Critical - App crashes or data wrong
- 🟠 High - Feature broken
- 🟡 Medium - Works but looks bad
- 🟢 Low - Minor polish needed

---

## Test Summary

| Category             | Passed | Failed | Skipped |
|----------------------|--------|--------|---------|
| Phase 1: Data        | /6     |        |         |
| Phase 2: Alpha       | /12    |        |         |
| Phase 3: Polish      | /17    |        |         |
| Phase 4: Quality     | /6     |        |         |
| Phase 5: UX          | /8     |        |         |
| Phase 6: Auth        | /3     |        |         |
| Cross-functional     | /11    |        |         |
| **TOTAL**            | /63    |        |         |

---

**Tester Name:** _______________  
**Test Date:** _______________  
**App Version:** Post-M016  
**Browser:** _______________  

---

*This checklist covers Milestones 1-16. Update after each major milestone.*
