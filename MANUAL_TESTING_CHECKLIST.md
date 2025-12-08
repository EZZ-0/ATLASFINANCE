# ATLAS FINANCIAL INTELLIGENCE
# COMPREHENSIVE MANUAL TESTING CHECKLIST

Version: 1.0
Date: December 8, 2024
Tester Name: ________________________________________________
Start Time: ___________________ End Time: ___________________


================================================================================
SECTION 1: LANDING PAGE
================================================================================

TEST 1.1 - Header Display
Description: Load app and verify main header is visible
Steps: Open browser, navigate to localhost:8501
Expected: "ATLAS FINANCIAL INTELLIGENCE" header visible at top
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 1.2 - Search Box
Description: Verify search/ticker input is functional
Steps: Click on the search or ticker input field
Expected: Dropdown or input field appears and accepts text
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 1.3 - S&P 500 Dropdown
Description: Verify company dropdown populates
Steps: Click the company selection dropdown
Expected: Full list of S&P 500 companies appears
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 1.4 - Sidebar Initial State
Description: Check sidebar starts collapsed
Steps: Fresh page load (clear cache first)
Expected: Sidebar is collapsed on initial load
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 1.5 - Sidebar Expand
Description: Verify sidebar can be expanded
Steps: Click the expand arrow or button
Expected: Sidebar opens and shows theme selector
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 1.6 - Theme Selector
Description: Verify theme changes work
Steps: Select a different theme from dropdown
Expected: Colors update across entire application
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 1 SUMMARY
Total Tests: 6
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 2: SEARCH AND EXTRACTION
================================================================================

TEST 2.1 - Large Cap Extraction (AAPL)
Ticker: AAPL
Steps: Enter AAPL in search, submit
Expected: Data loads in under 30 seconds with minimal N/A values
Load Time: __________ seconds
N/A Count: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 2.2 - Financial Sector (JPM)
Ticker: JPM
Steps: Enter JPM in search, submit
Expected: Bank-specific metrics appear (NIM, efficiency ratio, etc.)
Load Time: __________ seconds
Bank Metrics Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 2.3 - Smaller Company (FIVE)
Ticker: FIVE
Steps: Enter FIVE in search, submit
Expected: Data extracts successfully without errors
Load Time: __________ seconds
Errors: ____________________________________________________________________
Status: PASS / FAIL

TEST 2.4 - Tech Company (NVDA)
Ticker: NVDA
Steps: Enter NVDA in search, submit
Expected: Growth metrics populated correctly
Load Time: __________ seconds
Growth Metrics Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 2.5 - Retail Company (WMT)
Ticker: WMT
Steps: Enter WMT in search, submit
Expected: Inventory and retail metrics visible
Load Time: __________ seconds
Inventory Metrics Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 2 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 3: TAB 1 - DASHBOARD
================================================================================

TEST 3.1 - Dashboard Load
Steps: Click Dashboard tab after ticker extraction
Expected: Charts and metrics render without errors
Charts Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 3.2 - Flip Cards Display
Steps: Scroll to metrics section on dashboard
Expected: Cards show actual values, not "N/A"
Cards with Values: __________ out of __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 3.3 - Flip Card Animation
Steps: Hover mouse over any metric card
Expected: Card flips to show explanation on back
Animation Works: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 3.4 - Price Chart
Steps: Look at the main price chart
Expected: Current price line is visible and accurate
Price Displayed: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 3.5 - Key Metrics Accuracy
Steps: Compare revenue and EPS to Yahoo Finance
App Revenue: __________
Yahoo Revenue: __________
App EPS: __________
Yahoo EPS: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 3 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 4: TAB 2 - DATA
================================================================================

TEST 4.1 - Income Statement
Steps: Click Data tab, view income statement section
Expected: Revenue and Net Income are visible
Revenue Visible: YES / NO
Net Income Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 4.2 - Balance Sheet
Steps: Scroll down in Data tab to balance sheet
Expected: Total Assets and Total Liabilities shown
Assets Visible: YES / NO
Liabilities Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 4.3 - Cash Flow Statement
Steps: Scroll to cash flow section
Expected: Operating Cash Flow and CapEx visible
Operating CF Visible: YES / NO
CapEx Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 4.4 - Multi-Year Data
Steps: Check column headers in financial tables
Expected: 4-5 years of historical data shown
Years of Data: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 4.5 - Growth Rates
Steps: Find CAGR or growth rates section
Expected: Percentage values displayed for key metrics
Revenue CAGR: __________
EPS CAGR: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 4 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 5: TAB 3 - DEEP DIVE (ANALYSIS)
================================================================================

TEST 5.1 - Valuation Metrics
Steps: Click Deep Dive tab, check valuation section
Expected: PE, P/B, EV/EBITDA show actual values
PE Ratio: __________
P/B Ratio: __________
EV/EBITDA: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 5.2 - Profitability Metrics
Steps: Check profitability section
Expected: ROE, ROA, and margins are populated
ROE: __________
ROA: __________
Gross Margin: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 5.3 - Growth Quality
Steps: Check growth quality section
Expected: Revenue and EPS growth rates shown
Revenue Growth: __________
EPS Growth: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 5.4 - Flip Cards N/A Rate
Steps: Count flip cards showing N/A vs actual values
Expected: Less than 20% show N/A
Total Cards: __________
Cards with N/A: __________
N/A Percentage: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 5.5 - Balance Sheet Health
Steps: Check balance sheet health section
Expected: Current ratio and debt/equity shown
Current Ratio: __________
Debt/Equity: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 5.6 - Cash Flow Analysis
Steps: Check cash flow analysis section
Expected: FCF and OCF metrics visible
Free Cash Flow: __________
Operating Cash Flow: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 5 SUMMARY
Total Tests: 6
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 6: TAB 4 - VALUATION
================================================================================

TEST 6.1 - DCF Model Load
Steps: Click Valuation tab
Expected: DCF calculator loads properly
Calculator Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 6.2 - Input Sliders
Steps: Adjust the growth rate slider
Expected: Fair value updates dynamically
Initial Fair Value: __________
After Adjustment: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 6.3 - Sensitivity Table
Steps: Check sensitivity analysis table
Expected: Multiple scenarios shown with different assumptions
Scenarios Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 6.4 - Monte Carlo Simulation
Steps: Click run simulation button
Expected: Distribution chart appears
Chart Appears: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 6.5 - Earnings Revisions
Steps: Navigate to earnings revisions sub-tab
Expected: Analyst estimates shown
Estimates Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 6 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 7: TAB 5 - RISK AND OWNERSHIP
================================================================================

TEST 7.1 - Forensic Shield
Steps: Click Risk & Ownership tab, view Forensic Shield
Expected: Red flags analysis loads with Z-Score, M-Score, F-Score
Z-Score Visible: YES / NO
M-Score Visible: YES / NO
F-Score Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 7.2 - Corporate Governance
Steps: Click Corporate Governance sub-tab
Expected: Board info and ESG scores shown
Board Info Visible: YES / NO
ESG Scores Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 7.3 - Insider Activity
Steps: Click Insider Activity sub-tab
Expected: Buy/sell transactions displayed
Transactions Visible: YES / NO
Sentiment Score: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 7.4 - Institutional Ownership
Steps: Click Inst. Ownership sub-tab
Expected: Top holders and ownership percentage shown
Top Holders Visible: YES / NO
Ownership Percentage: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 7.5 - Error Handling
Steps: Navigate through all sub-tabs rapidly
Expected: No crashes or NoneType error messages
Errors Encountered: ________________________________________________________
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 7 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 8: TAB 6 - MARKET INTEL
================================================================================

TEST 8.1 - Technical Analysis
Steps: Click Market Intel tab
Expected: Moving averages and RSI indicators shown
50-Day MA: __________
200-Day MA: __________
RSI: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 8.2 - Options Flow
Steps: Check options section
Expected: Put/call ratio displayed if available
Put/Call Ratio: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 8.3 - Peer Discovery
Steps: Check peer comparison section
Expected: Similar companies auto-discovered
Peers Found: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 8.4 - Peer Comparison
Steps: Select a peer company for comparison
Expected: Side-by-side metrics comparison displays
Comparison Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 8.5 - Quant Analysis
Steps: Check quantitative analysis section
Expected: Fama-French factors shown
Factors Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 8 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 9: TAB 7 - NEWS
================================================================================

TEST 9.1 - News Load
Steps: Click News tab
Expected: Recent articles appear
Articles Visible: YES / NO
Article Count: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 9.2 - Sentiment Indicators
Steps: Check article sentiment colors
Expected: Positive/negative indicated by color coding
Colors Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 9.3 - Article Links
Steps: Click on an article headline
Expected: Opens article in new browser tab
Link Works: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 9 SUMMARY
Total Tests: 3
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 10: TAB 8 - IC MEMO
================================================================================

TEST 10.1 - Memo Generation
Steps: Click IC Memo tab
Expected: Investment memo loads with content
Memo Loads: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 10.2 - AI Analysis Content
Steps: Review memo content
Expected: Bullet points and recommendations present
Recommendations Visible: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 10.3 - PDF Export
Steps: Click PDF export button
Expected: PDF file downloads successfully
PDF Downloaded: YES / NO
File Name: __________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 10.4 - All Sections Present
Steps: Scroll through entire memo
Expected: Strengths, risks, and conclusion sections visible
Strengths Section: YES / NO
Risks Section: YES / NO
Conclusion Section: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 10 SUMMARY
Total Tests: 4
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 11: UI/UX CHECKS
================================================================================

TEST 11.1 - Sidebar Collapse
Steps: Click X or collapse button on sidebar
Expected: Sidebar closes smoothly
Closes Properly: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 11.2 - Sidebar Expand
Steps: Click arrow or expand button
Expected: Sidebar opens properly
Opens Properly: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 11.3 - Icon Display
Steps: Check all buttons and icons throughout app
Expected: Shows actual icons, not emoji code text
Icons Render Correctly: YES / NO
Problem Areas: _____________________________________________________________
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 11.4 - Responsive Layout
Steps: Resize browser window to different sizes
Expected: Layout adjusts appropriately
Adjusts Correctly: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 11.5 - Theme Persistence
Steps: Change theme, then switch between tabs
Expected: Theme stays consistent across all tabs
Theme Persists: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 11 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 12: EDGE CASES
================================================================================

TEST 12.1 - Invalid Ticker
Ticker: XXXXX
Steps: Enter invalid ticker XXXXX
Expected: Error message displays, app does not crash
Error Message: _____________________________________________________________
App Crashed: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 12.2 - No Data Company
Ticker: __________ (use obscure OTC)
Steps: Enter a ticker with minimal data
Expected: Graceful handling with N/A where needed
Handled Gracefully: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 12.3 - Fast Ticker Switch
Steps: Enter AAPL, immediately switch to MSFT
Expected: No stale AAPL data shown for MSFT
Stale Data: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

TEST 12.4 - Page Refresh
Steps: Press F5 to refresh page
Expected: Returns to landing page cleanly
Returns to Landing: YES / NO
Result: ____________________________________________________________________
Status: PASS / FAIL

SECTION 12 SUMMARY
Total Tests: 4
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
SECTION 13: DATA ACCURACY SPOT CHECK
================================================================================

Use AAPL for all accuracy checks. Compare values to Yahoo Finance.

TEST 13.1 - Revenue Accuracy
App Value: __________
Yahoo Finance Value: __________
Difference: __________
Acceptable (within 5%): YES / NO
Status: PASS / FAIL

TEST 13.2 - Net Income Accuracy
App Value: __________
Yahoo Finance Value: __________
Difference: __________
Acceptable (within 5%): YES / NO
Status: PASS / FAIL

TEST 13.3 - PE Ratio Accuracy
App Value: __________
Yahoo Finance Value: __________
Difference: __________
Acceptable (within 10%): YES / NO
Status: PASS / FAIL

TEST 13.4 - Market Cap Accuracy
App Value: __________
Yahoo Finance Value: __________
Difference: __________
Acceptable (within 5%): YES / NO
Status: PASS / FAIL

TEST 13.5 - Dividend Yield Accuracy
App Value: __________
Yahoo Finance Value: __________
Difference: __________
Acceptable (within 0.1%): YES / NO
Status: PASS / FAIL

SECTION 13 SUMMARY
Total Tests: 5
Passed: _____
Failed: _____
Notes: _____________________________________________________________________


================================================================================
FINAL SUMMARY
================================================================================

Section 1 - Landing Page:        _____ / 6 passed
Section 2 - Search/Extraction:   _____ / 5 passed
Section 3 - Dashboard:           _____ / 5 passed
Section 4 - Data Tab:            _____ / 5 passed
Section 5 - Deep Dive:           _____ / 6 passed
Section 6 - Valuation:           _____ / 5 passed
Section 7 - Risk/Ownership:      _____ / 5 passed
Section 8 - Market Intel:        _____ / 5 passed
Section 9 - News:                _____ / 3 passed
Section 10 - IC Memo:            _____ / 4 passed
Section 11 - UI/UX:              _____ / 5 passed
Section 12 - Edge Cases:         _____ / 4 passed
Section 13 - Data Accuracy:      _____ / 5 passed

TOTAL:                           _____ / 63 passed

PASS RATE:                       _____ %


================================================================================
PASS CRITERIA
================================================================================

CRITICAL TESTS (Must Pass):
- Tests 1.1 through 2.5 (Landing and Extraction)
- Tests 5.1 through 5.6 (Deep Dive Analysis)
- Tests 7.1 through 7.5 (Risk and Ownership)
- Tests 11.1 through 11.3 (UI/UX)

MINIMUM REQUIREMENTS:
- Overall pass rate must be greater than 90%
- N/A values must be less than 10% of metrics
- Extraction time must be under 30 seconds


================================================================================
BUG REPORT
================================================================================

Bug 1:
Test Number: __________
Ticker Used: __________
Tab/Section: __________
Expected: ________________________________________________________________
Actual: __________________________________________________________________
Console Error: ____________________________________________________________

Bug 2:
Test Number: __________
Ticker Used: __________
Tab/Section: __________
Expected: ________________________________________________________________
Actual: __________________________________________________________________
Console Error: ____________________________________________________________

Bug 3:
Test Number: __________
Ticker Used: __________
Tab/Section: __________
Expected: ________________________________________________________________
Actual: __________________________________________________________________
Console Error: ____________________________________________________________


================================================================================
SIGN-OFF
================================================================================

Testing Completed: YES / NO
Overall Result: PASS / FAIL
Critical Issues Found: _____________________________________________________
Recommendations: ___________________________________________________________

Tester Signature: __________________________________________________________
Date: __________
Time: __________


================================================================================
END OF TESTING CHECKLIST
================================================================================
