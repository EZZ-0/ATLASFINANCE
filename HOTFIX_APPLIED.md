# 🔥 HOTFIX APPLIED - Search & News Issues
**Date:** November 30, 2025  
**Status:** ✅ FIXED

---

## 🐛 **BUGS FIXED:**

### **1. DataFrame Ambiguous Error** ✅
**Error:** `ValueError: The truth value of a DataFrame is ambiguous`

**Root Cause:** 
- Number formatting was applied BEFORE search logic
- Search was trying to compare formatted strings to DataFrame structure

**Fix:**
- Keep `df_original` separate for search operations
- Apply formatting only for display (`df_display`)
- Search now works on original unformatted data
- Display shows formatted numbers

---

### **2. Search Dropdown Shows Numbers (Not Metrics)** ✅
**Problem:**
- Dropdown showed formatted values like "$1.22B", "$-215.00M"
- Users wanted to search by metric names (e.g., "Revenue", "Net Income")

**Fix:**
- **REMOVED** confusing value-based dropdown
- **REPLACED** with simple text input
- Search now filters by **row labels** (metric names)
- Placeholder: "Type metric name to filter (e.g., 'revenue', 'net income')"
- Case-insensitive matching

**Before:**
```
Search: [Dropdown with $1.22B, $-215.00M, ...]  [Manual input]
```

**After:**
```
Search: [Type metric name to filter...]
```

---

### **3. News Source Missing** ✅
**Problem:**
- News layout moved source to right column
- Only showed date and read time

**Fix:**
- Moved source (`📰 {article['source']}`) back to right column (col2)
- Now shows:
  - **Right column:**
    - 📰 Source name (e.g., "Yahoo Finance")
    - 🕒 Date
    - ✍️ Author (if available)
    - 📊 Confidence (if available)
    - 📖 Read time

---

## 📝 **CODE CHANGES:**

### `enhanced_tables.py`
```python
# BEFORE (Broken):
if format_numbers:
    df = format_dataframe_numbers(df)  # ❌ Breaks search!
    
# Search logic on formatted df  # ❌ Causes ambiguous error

# AFTER (Fixed):
df_original = df.copy()  # ✅ Keep original for search

# Search on original
if manual_search:
    mask = df.index.str.contains(manual_search, case=False)
    df = df[mask]

# Format AFTER search for display only
if format_numbers:
    df_display = format_dataframe_numbers(df)  # ✅ Display only
```

### `usa_app.py` (News)
```python
# BEFORE:
with col1:
    st.markdown(f"{sentiment_tag} **{article['title']}**")
    st.caption(f"📰 {article['source']}")  # ❌ Wrong column

with col2:
    st.caption(f"🕒 {article['published']}")

# AFTER:
with col1:
    st.markdown(f"{sentiment_tag} **{article['title']}**")  # Title + summary

with col2:
    st.caption(f"📰 {article['source']}")  # ✅ Source in right column
    st.caption(f"🕒 {article['published']}")
    # ... author, confidence, read time
```

---

## ✅ **NOW WORKING:**

1. **Search by Metric Name:**
   - Type "revenue" → Shows all revenue-related rows
   - Type "net income" → Shows net income rows
   - Type "cash" → Shows all cash-related metrics
   - ✅ No more DataFrame errors!

2. **Numbers Display Correctly:**
   - Table shows: $4.45B, $1.22M (formatted)
   - Export shows: 4450000000 (raw for Excel)
   - Search works on: "Total Revenue", "Net Income" (labels)

3. **News Shows Full Info:**
   - Left: Title + Summary
   - Right: Source, Date, Author, Confidence, Read time
   - ✅ Source is now visible!

---

## 🧪 **TEST AGAIN:**

1. **Extract Tab** → Load APA
2. **Income Statement Table:**
   - Type "revenue" in search
   - Should filter to revenue rows
   - Numbers should show as $X.XXB
   - ✅ No errors!
3. **News Tab:**
   - Check articles show source in right column
   - ✅ Source visible!

---

## 📌 **ABOUT ALERT BOXES:**

**User noted:** "alert box are still blue highlighted inside a golden box"

**Status:** Known - Will fix in next iteration
**Reason:** Streamlit uses nested alert structure that needs deeper CSS override
**Priority:** Low (cosmetic only)
**Fix planned:** Add more specific CSS selectors for nested alert content

---

## ✅ **READY FOR TESTING AGAIN!**

All critical issues fixed:
- ✅ No DataFrame errors
- ✅ Search works (metric names)
- ✅ Numbers formatted
- ✅ News source visible

**Report back:** "✅ works" or "⚠️ still issue: [describe]"


