# ATLAS Testing Checkpoint
## Manual Testing Checklist - All Milestones

**Generated:** 2025-12-08  
**Version:** Post M016 (Auth Complete)  
**Monetization Flag:** OFF (Free access for testers)

---

## How to Test

1. Run the app: `streamlit run usa_app.py`
2. Open browser to `http://localhost:8501`
3. Follow checklist below
4. Mark items ✅ or ❌
5. Note any bugs in the Issues section at bottom

---

## PHASE 1: Data Foundation (M001)

### WACC & DCF Calculations
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 1.1 | WACC displays | Search AAPL → DCF tab | WACC shown with breakdown | ⬜ |
| 1.2 | Beta is adjusted | Check WACC details | Should show "Adjusted Beta" not raw | ⬜ |
| 1.3 | Risk-free rate | Check WACC details | Should be ~4-5% (current Treasury) | ⬜ |
| 1.4 | FCF methods | DCF tab dropdown | 4 FCF calculation options available | ⬜ |

### Industry Benchmarks
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 1.5 | Sector shown | Dashboard or Summary | Company sector displayed | ⬜ |
| 1.6 | Benchmarks work | Valuation tab | Industry comparison shown | ⬜ |

---

## PHASE 2: Alpha Signals (M002-M004)

### Earnings Revisions (M002)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 2.1 | Tab exists | Click "Earnings Revisions" tab | Tab loads without error | ⬜ |
| 2.2 | Data displays | Check AAPL revisions | Shows analyst estimate changes | ⬜ |
| 2.3 | Trend indicator | Look for momentum | Shows up/down/flat trend | ⬜ |

### Insider Transactions (M003)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 3.1 | Tab exists | Click "Insider" tab | Tab loads without error | ⬜ |
| 3.2 | Summary shown | Check insider section | Buy/Sell counts, net value | ⬜ |
| 3.3 | Sentiment gauge | Look for gauge chart | Shows bullish/bearish sentiment | ⬜ |
| 3.4 | Transaction list | Expand transactions | Recent insider trades listed | ⬜ |

### Institutional Ownership (M004)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 4.1 | Tab exists | Click "Ownership" tab | Tab loads without error | ⬜ |
| 4.2 | Percentages shown | Check ownership section | Institutional %, Insider % | ⬜ |
| 4.3 | Top holders | Expand holders list | Top 10 institutions listed | ⬜ |
| 4.4 | Accumulation signal | Look for signal | Shows accumulating/distributing | ⬜ |

---

## PHASE 3: Professional Polish (M005-M008)

### PDF Export (M005)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 5.1 | Export button | Investment Summary tab | "Download PDF" button visible | ⬜ |
| 5.2 | PDF generates | Click download | PDF file downloads | ⬜ |
| 5.3 | PDF readable | Open downloaded PDF | Content is formatted correctly | ⬜ |
| 5.4 | Enhanced option | Select "Enhanced IC Memo" | Different PDF format available | ⬜ |

### White-Label Themes (M006)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 6.1 | Theme selector | Sidebar control panel | Theme dropdown visible | ⬜ |
| 6.2 | Dark theme | Select "Atlas Dark" | Dark theme applies | ⬜ |
| 6.3 | Light theme | Select "Atlas Light" | Light theme applies | ⬜ |
| 6.4 | Theme persists | Change tabs | Theme stays same | ⬜ |

### Performance (M007)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 7.1 | Initial load | Open app fresh | Loads in < 10 seconds | ⬜ |
| 7.2 | Ticker search | Search new ticker | Data loads in < 5 seconds | ⬜ |
| 7.3 | Tab switching | Click between tabs | Switches in < 2 seconds | ⬜ |
| 7.4 | Cached reload | Search same ticker again | Loads in < 2 seconds | ⬜ |

### Flip Cards (M008)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 8.1 | Cards visible | Dashboard tab | Metric cards displayed | ⬜ |
| 8.2 | Click to flip | Click any card | Card flips with animation | ⬜ |
| 8.3 | Formula shown | View flipped card | Shows formula/equation | ⬜ |
| 8.4 | Insight shown | View flipped card | Shows interpretation text | ⬜ |
| 8.5 | Colors correct | Check card colors | Green=good, Red=bad, Yellow=neutral | ⬜ |

---

## PHASE 4: Data Quality (M011-M013)

### Ticker Handling
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 11.1 | Valid ticker | Search "AAPL" | Data loads correctly | ⬜ |
| 11.2 | Invalid ticker | Search "XXXXX" | Shows error message | ⬜ |
| 11.3 | Case insensitive | Search "aapl" | Works same as "AAPL" | ⬜ |

### Bank Metrics (M012)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 12.1 | Bank detection | Search "JPM" | Loads without errors | ⬜ |
| 12.2 | Bank metrics | Check Dashboard | Shows P/B instead of D/E | ⬜ |
| 12.3 | No FCF shown | Check bank Dashboard | FCF not shown (or shows Dividend Yield) | ⬜ |

---

## PHASE 5: UX (M014-M015)

### Draggable Dashboard (M014)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 14.1 | Reorder control | Dashboard tab | "Customize Layout" expander visible | ⬜ |
| 14.2 | Presets work | Select "Valuation Focus" | Layout changes | ⬜ |
| 14.3 | Reset works | Click "Reset to Default" | Original layout restored | ⬜ |

### Mobile Responsive (M015)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 15.1 | Desktop view | Normal browser window | 5-column layout | ⬜ |
| 15.2 | Tablet view | Resize to ~768px width | 2-3 column layout | ⬜ |
| 15.3 | Mobile view | Resize to ~400px width | Single column layout | ⬜ |
| 15.4 | Touch targets | Mobile view | Buttons are large enough to tap | ⬜ |

---

## PHASE 6: Monetization (M016)

### Auth System (Currently OFF)
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| 16.1 | No login required | Open app | App loads without login prompt | ⬜ |
| 16.2 | No limits | Run 10+ analyses | No usage limit warnings | ⬜ |
| 16.3 | All features work | Try PDF, Monte Carlo, etc. | Everything accessible | ⬜ |

**Note:** Auth is behind `MONETIZATION_ENABLED=false` flag. When enabled:
- Login/register forms appear
- Usage limits enforced
- Upgrade prompts shown

---

## Cross-Functional Tests

### General App Health
| # | Test | Steps | Expected | Status |
|---|------|-------|----------|--------|
| X.1 | No console errors | Open browser dev tools | No red errors in console | ⬜ |
| X.2 | All tabs load | Click every tab | No crashes or errors | ⬜ |
| X.3 | Multiple tickers | Search 5 different tickers | All load correctly | ⬜ |
| X.4 | S&P 500 dropdown | Select from dropdown | Loads selected company | ⬜ |

### Test Tickers (Diverse Coverage)
| Ticker | Type | Status |
|--------|------|--------|
| AAPL | Tech mega-cap | ⬜ |
| JPM | Bank | ⬜ |
| XOM | Energy | ⬜ |
| TSLA | Growth (no dividend) | ⬜ |
| KO | Consumer staples | ⬜ |
| NVDA | Semiconductor | ⬜ |
| JNJ | Healthcare | ⬜ |

---

## Issues Found

| # | Description | Severity | Milestone |
|---|-------------|----------|-----------|
| | | | |
| | | | |
| | | | |

**Severity Levels:**
- 🔴 Critical - App crashes or data wrong
- 🟠 High - Feature broken
- 🟡 Medium - Works but looks bad
- 🟢 Low - Minor polish needed

---

## Test Summary

| Category | Passed | Failed | Skipped |
|----------|--------|--------|---------|
| Phase 1: Data | /6 | | |
| Phase 2: Alpha | /12 | | |
| Phase 3: Polish | /17 | | |
| Phase 4: Quality | /6 | | |
| Phase 5: UX | /8 | | |
| Phase 6: Auth | /3 | | |
| Cross-functional | /11 | | |
| **TOTAL** | /63 | | |

---

**Tester Name:** _______________  
**Test Date:** _______________  
**App Version:** Post-M016  
**Browser:** _______________  

---

*This checklist covers Milestones 1-16. Update after each major milestone.*

