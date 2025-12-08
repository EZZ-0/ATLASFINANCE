# 🎛️ LIVE DCF MODELING - QUICK START GUIDE

**For:** First-time users  
**Time:** 5 minutes  
**Difficulty:** Easy

---

## 🚀 **HOW TO USE:**

### **Step 1: Extract Data** (30 seconds)
```
1. Open sidebar
2. Enter ticker: AAPL
3. Click "🔍 SEARCH"
4. Wait for extraction
```

### **Step 2: Open Live Builder** (10 seconds)
```
1. Click "Model" tab
2. Click "🎛️ Live Scenario Builder" sub-tab
```

### **Step 3: Choose Your Starting Point** (10 seconds)
```
Select from dropdown:
┌─────────────────────┐
│ Base Case        ▼ │  ← Most common
├─────────────────────┤
│ Conservative       │  ← Lower growth
│ Aggressive         │  ← Higher growth
│ Custom             │  ← Blank slate
└─────────────────────┘
```

### **Step 4: Adjust Sliders** (60 seconds)
```
Growth Section:
Year 1 Growth: ━━━━━●━━━━ 12%
Year 2 Growth: ━━━━●━━━━━ 10%
Year 3 Growth: ━━━●━━━━━━  8%
Year 4 Growth: ━━●━━━━━━━  6%
Year 5 Growth: ━●━━━━━━━━  5%

Valuation Section:
WACC:          ━━━━━●━━━━ 10%
Terminal:      ━●━━━━━━━━  2%
Tax Rate:      ━━━━●━━━━━ 21%

Operating Section:
CapEx:         ━━●━━━━━━━  5%
NWC Change:    ━●━━━━━━━━  2%
```

### **Step 5: See Quick Preview** (instant)
```
📊 Quick Preview:
┌──────────────────┬────────────┐
│ Est. EV          │ $3.2T      │
│ Avg Growth       │ 8.2%       │
│ WACC             │ 10.0%      │
│ Sensitivity      │ +1.5%      │
└──────────────────┴────────────┘
```

### **Step 6: Run Full DCF** (2 seconds)
```
Click this big button:
┌───────────────────────────────────┐
│ 🚀 Run Full DCF with Custom Inputs│
└───────────────────────────────────┘

Wait 2 seconds... ✅ Done!
```

### **Step 7: View Results** (30 seconds)
```
✅ Custom Scenario Results:
┌──────────────┬─────────┬──────────┬──────────┐
│ EV           │ Equity  │ Val/Share│ Upside   │
├──────────────┼─────────┼──────────┼──────────┤
│ $3.2T        │ $3.1T   │ $220.50  │ +18.5%   │
└──────────────┴─────────┴──────────┴──────────┘

📊 Compare to Presets:
┌──────────────┬───────────┐
│ Scenario     │ Val/Share │
├──────────────┼───────────┤
│ Conservative │ $180.50   │
│ Base         │ $210.75   │
│ Aggressive   │ $250.25   │
│ Your Custom  │ $220.50   │ ← You are here
└──────────────┴───────────┘
```

### **Step 8: Save Scenario** (20 seconds) - OPTIONAL
```
Click: [💾 Save This Scenario]
Enter name: "My Bull Case"
Click: [Confirm Save]
✅ Saved!
```

### **Step 9: Load Later** (10 seconds) - OPTIONAL
```
Click: [📂 Load]
See list:
┌─────────────────────────────────┐
│ My Bull Case                    │
│ Saved: 2025-12-01 15:30        │
│              [Load]  [🗑️]       │
└─────────────────────────────────┘
Click: [Load] → Sliders populate!
```

### **Step 10: Export** (10 seconds) - OPTIONAL
```
[📥 Export Comparison (CSV)]  ← Spreadsheet
[📄 Generate PDF Report]      ← Professional doc
```

---

## 💡 **TIPS & TRICKS:**

### **Tip 1: Start with Base Case**
- Most realistic starting point
- Good for first-time users
- Easy to adjust from there

### **Tip 2: Adjust 1-2 Parameters at a Time**
- Don't change everything at once
- See impact of each change
- Build intuition gradually

### **Tip 3: Use Quick Preview**
- No need to run full DCF every time
- Quick preview gives good sense
- Full DCF only when you're ready

### **Tip 4: Save Multiple Scenarios**
- Bull case (optimistic)
- Base case (realistic)
- Bear case (pessimistic)
- Build a scenario library!

### **Tip 5: Compare Results**
- Always check comparison table
- See where your scenario ranks
- Understand your assumptions

---

## 🎯 **COMMON SCENARIOS:**

### **Scenario 1: "Tech Boom" (Optimistic)**
```
Use Case: Bull market, tech stock
Settings:
  Year 1-3 Growth: 15-20%
  WACC: 8-9%
  Terminal: 3-3.5%
Expected: High valuation
```

### **Scenario 2: "Recession" (Pessimistic)**
```
Use Case: Bear market, economic downturn
Settings:
  Year 1 Growth: -5% to 0%
  WACC: 12-15%
  Terminal: 1-2%
Expected: Low valuation
```

### **Scenario 3: "Steady Growth" (Conservative)**
```
Use Case: Mature company, stable industry
Settings:
  Year 1-5 Growth: 3-5%
  WACC: 10-11%
  Terminal: 2%
Expected: Moderate valuation
```

### **Scenario 4: "Turnaround" (Mixed)**
```
Use Case: Company recovery
Settings:
  Year 1: -5%
  Year 2-3: 5-10%
  Year 4-5: 10-15%
  WACC: 11%
Expected: Value emerges over time
```

---

## ⚠️ **COMMON MISTAKES:**

### **Mistake 1: Unrealistic Growth**
❌ Don't set: Year 1: 50%, Year 2: 50%, ...
✅ Do set: Year 1: 15%, Year 2: 12%, Year 3: 10%, ...
**Why:** Growth typically decays to terminal rate

### **Mistake 2: Terminal > 5%**
❌ Don't set: Terminal Growth = 7%
✅ Do set: Terminal Growth = 2-3%
**Why:** Long-term GDP growth ~2-3%

### **Mistake 3: WACC Too Low**
❌ Don't set: WACC = 3%
✅ Do set: WACC = 8-12%
**Why:** Cost of capital typically 8-15%

### **Mistake 4: Ignoring Quick Preview**
❌ Don't: Adjust sliders → Run DCF immediately
✅ Do: Adjust sliders → Check preview → Iterate → Run DCF
**Why:** Saves time, builds intuition

---

## 🔧 **TROUBLESHOOTING:**

### **Issue 1: Sliders not responding**
**Solution:**
- Refresh page
- Re-extract ticker
- Check console for errors

### **Issue 2: "Run DCF" button does nothing**
**Solution:**
- Wait 2-3 seconds (it's calculating)
- Look for spinner/loading indicator
- Check for error message

### **Issue 3: Can't save scenario**
**Solution:**
- Make sure `saved_scenarios/` folder exists
- Check write permissions
- Use simple scenario name (no special chars)

### **Issue 4: Can't load scenario**
**Solution:**
- Make sure you saved for the current ticker
- Refresh scenario list
- Check file exists in `saved_scenarios/`

### **Issue 5: PDF won't generate**
**Solution:**
- Make sure `reportlab` is installed
- Run: `pip install reportlab`
- Restart Streamlit app

---

## 📊 **UNDERSTANDING THE OUTPUTS:**

### **Quick Preview Metrics:**

**Est. Enterprise Value**
- Fast estimate using revenue multiple
- Gives ballpark valuation
- Updates instantly as you adjust

**Avg Growth (5Y)**
- Average of Year 1-5 growth rates
- Shows overall growth trajectory
- Higher = more optimistic

**WACC**
- Current discount rate setting
- Higher WACC = lower valuation
- Represents cost of capital

**Value Sensitivity**
- Est. % change from WACC adjustment
- Shows how sensitive value is to WACC
- Higher sensitivity = more risk

### **Full DCF Results:**

**Enterprise Value**
- Total value of the business
- Includes debt + equity
- Used for M&A pricing

**Equity Value**
- Value available to shareholders
- EV - Net Debt
- Used for stock valuation

**Value Per Share**
- Equity Value ÷ Shares Outstanding
- Compare to current stock price
- Key output for investors

**Upside/Downside**
- % difference from current price
- Positive = undervalued
- Negative = overvalued

---

## 🎓 **LEARNING PATH:**

### **Beginner (Week 1):**
1. Use presets only (Base/Conservative/Aggressive)
2. Understand what each slider does
3. Run 5-10 DCFs on different tickers
4. Compare results across scenarios

### **Intermediate (Week 2-3):**
1. Start adjusting 1-2 sliders
2. Save your first custom scenarios
3. Build scenario library (3-5 scenarios per ticker)
4. Export CSV comparisons

### **Advanced (Week 4+):**
1. Create fully custom scenarios
2. Test edge cases (recession, boom)
3. Generate PDF reports
4. Present findings to others

---

## 📝 **CHECKLIST FOR DEMO:**

**Before Demo:**
- [  ] Test extraction (pick reliable ticker)
- [  ] Verify sliders work
- [  ] Save a sample scenario
- [  ] Generate a sample PDF

**During Demo:**
1. [  ] Extract ticker quickly
2. [  ] Navigate to Live Builder
3. [  ] Adjust 2-3 sliders
4. [  ] Point out quick preview
5. [  ] Run full DCF
6. [  ] Show comparison table
7. [  ] Save scenario
8. [  ] Generate PDF

**After Demo:**
- [  ] Answer questions confidently
- [  ] Offer to email PDF
- [  ] Highlight key features

---

## 🏆 **SUCCESS METRICS:**

**You know it's working when:**
- ✅ Quick preview updates instantly
- ✅ Full DCF completes in 2-3 seconds
- ✅ Results display correctly
- ✅ Scenarios save/load smoothly
- ✅ PDF downloads successfully

**You're a power user when:**
- ✅ You have 5+ saved scenarios
- ✅ You can explain each slider's impact
- ✅ You compare multiple scenarios easily
- ✅ You generate PDFs regularly
- ✅ You demo confidently

---

## 📞 **GET HELP:**

**Documentation:**
- `LIVE_DCF_100_PERCENT_COMPLETE.md` - Full details
- `PDF_EXPORT_GUIDE.md` - PDF instructions
- This file - Quick start

**Test Script:**
- `test_live_dcf.bat` - Launch with guide

**Issues?**
- Check console for errors
- Re-read this guide
- Try a different ticker

---

**🎯 You're ready to use Live DCF Modeling!**

**Start now:** `streamlit run usa_app.py` → Model → Live Builder 🚀


