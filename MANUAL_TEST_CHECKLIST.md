# 🧪 MANUAL TEST CHECKLIST
## Investment Summary - Visual & Data Accuracy Validation

**Date:** _______________  
**Tester:** _______________  
**Automated Logic Tests:** ✅ PASSED (run `run_logic_tests.bat` first!)

---

## 📋 **QUICK 10-MINUTE MANUAL TEST**

### **Step 1: Visual Quality Check** (3 min)

**Launch App:**
```bash
streamlit run usa_app.py
```

**Extract AAPL:**
1. [ ] Select "AAPL - Apple Inc." from dropdown
2. [ ] Click "Extract Financial Data"
3. [ ] Wait for extraction to complete

**Navigate to Investment Summary (Tab #8):**
4. [ ] Tab exists and is clickable
5. [ ] Page loads without errors

**Visual Inspection:**
6. [ ] **Blue theme** applied (navy/blue backgrounds, not brown/gold)
7. [ ] **Header** displays properly with gradient blue text
8. [ ] **Bull Case** section (left column) has:
   - [ ] Green border/accent
   - [ ] 3 bullet points visible
   - [ ] Text is readable
9. [ ] **Bear Case** section (right column) has:
   - [ ] Red border/accent
   - [ ] 3 bullet points visible
   - [ ] Text is readable
10. [ ] **Key Metrics** section shows:
    - [ ] 8 metrics in 2 rows of 4
    - [ ] Values populated (not all "N/A")
11. [ ] **Risk Assessment** shows:
    - [ ] 5 risk cards side-by-side
    - [ ] Color circles visible (🟢🟡🔴)
    - [ ] Risk levels displayed (LOW/MODERATE/HIGH)
12. [ ] **Valuation Range** shows:
    - [ ] 3 cards (Bear/Base/Bull)
    - [ ] Dollar amounts visible
    - [ ] Percentages visible
13. [ ] **Red Flags** section shows:
    - [ ] At least 1 line of text
    - [ ] Either warnings or "No major red flags"

**UI Quality:**
14. [ ] No overlapping text
15. [ ] All sections properly aligned
16. [ ] Professional appearance (Bloomberg-style)
17. [ ] Mobile/responsive design works (resize browser)

---

### **Step 2: Data Accuracy Spot-Check** (5 min)

**Cross-Tab Consistency:**

1. [ ] Note AAPL's **ROE** from Investment Summary (Bull or Bear case)
   - Noted value: _________%

2. [ ] Go to **Extract** tab (Tab #1) → **Ratios** subtab
   - Find ROE in the table
   - Value: _________%
   - [ ] **MATCHES** Investment Summary? (within 1% rounding)

3. [ ] Note AAPL's **P/E Ratio** from Investment Summary (Key Metrics)
   - Noted value: _________x

4. [ ] Still in Extract → Ratios
   - Find P/E Ratio
   - Value: _________x
   - [ ] **MATCHES** Investment Summary? (within 1 point)

5. [ ] Note **Current Price** from Investment Summary
   - Value: $_________

6. [ ] Go to **Dashboard** tab (Tab #9)
   - Check Current Price metric
   - Value: $_________
   - [ ] **MATCHES** Investment Summary? (exact match)

**External Validation (Optional but Recommended):**

7. [ ] Open Yahoo Finance in browser: https://finance.yahoo.com/quote/AAPL
8. [ ] Compare **P/E Ratio**:
   - Yahoo Finance: _________x
   - Our App: _________x
   - [ ] Within 10% difference? (APIs may differ slightly)

---

### **Step 3: Intelligence Quality Check** (2 min)

**Read the Insights:**

1. [ ] Read all 3 **Bull Case** points
   - [ ] Do they sound intelligent (not generic)?
   - [ ] Do they mention specific numbers/percentages?
   - [ ] Do they make logical sense for AAPL?

2. [ ] Read all 3 **Bear Case** points
   - [ ] Do they sound like real concerns?
   - [ ] Do they mention specific numbers/percentages?
   - [ ] Do they make sense (not contradictory)?

3. [ ] Check **Risk Assessment** colors:
   - [ ] Do the risk levels make intuitive sense?
   - [ ] If Financial Health is GREEN, does AAPL have low debt/good liquidity?
   - [ ] If Valuation is YELLOW/RED, is P/E > 25?

4. [ ] Check **Red Flags**:
   - [ ] For AAPL (healthy company), should show "✅ No major red flags"
   - [ ] If warnings appear, do they make sense?

---

### **Step 4: Test High-Leverage Company** (Optional - 3 min)

**Extract F (Ford):**
1. [ ] Go back to Extract tab
2. [ ] Select "F - Ford Motor Company"
3. [ ] Extract data
4. [ ] Go to Investment Summary

**Verify Warnings:**
5. [ ] **Bear Case** mentions "debt" or "leverage"? (Should for Ford!)
6. [ ] **Risk Assessment**: Financial Health = 🔴 HIGH or 🟡 MODERATE?
7. [ ] **Red Flags**: Shows "⚠️ High leverage" warning?
8. [ ] **Key Metrics**: Debt/Equity > 1.5? (typical for Ford)

---

## ✅ **PASS/FAIL DECISION**

### **PASS if ALL true:**
- [ ] No Python errors/crashes
- [ ] Blue theme fully applied
- [ ] All 6 sections render correctly
- [ ] Data matches across tabs (ROE, P/E, Price)
- [ ] Bull/Bear points are intelligent and specific
- [ ] Risk colors make logical sense
- [ ] High-leverage company (F) triggers appropriate warnings

### **FAIL if ANY true:**
- [ ] Python error appears
- [ ] Data mismatch (>10% difference)
- [ ] Logic error (healthy company shows HIGH risks)
- [ ] Visual bugs (broken layout, unreadable text)
- [ ] Generic insights (too vague, no numbers)

---

## 📊 **FINAL VERDICT**

**Overall Status:** 
- [ ] ✅ **PASS** - Production ready!
- [ ] ⚠️ **CONDITIONAL PASS** - Minor issues, document below
- [ ] ❌ **FAIL** - Critical issues, needs fixes

**Notes/Issues Found:**
```
____________________________________________________________
____________________________________________________________
____________________________________________________________
```

**Action Items:**
```
____________________________________________________________
____________________________________________________________
____________________________________________________________
```

---

## 🎯 **CONFIDENCE LEVEL**

After completing this checklist:

- [ ] **100% Confident** - Ready to deploy, no concerns
- [ ] **95% Confident** - Very minor cosmetic issues only
- [ ] **<90% Confident** - Review and fix issues first

---

**Signature:** _______________  
**Date/Time:** _______________

---

## 📝 **APPENDIX: Known Good Values for AAPL**

*(As of data extraction date - may vary slightly)*

- **ROE:** ~150-160%
- **P/E Ratio:** ~30-35x
- **Current Price:** Check Yahoo Finance for current
- **Gross Margin:** ~45-46%
- **Debt/Equity:** ~1.5-2.0
- **Current Ratio:** ~0.9-1.1

Use these as sanity checks during your testing!


