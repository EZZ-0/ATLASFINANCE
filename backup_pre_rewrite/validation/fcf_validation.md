# FCF Calculator Validation Report - TASK-E009

**Validated By:** Executor  
**Date:** 2025-12-07  
**Module:** calculations/fcf_calculator.py  
**Depends On:** TASK-A004 (Complete)

---

## 1. Executive Summary

| Method | Formula Correct | Test Passed | Edge Cases | Overall |
|--------|-----------------|-------------|------------|---------|
| Simple FCF | ✅ | ✅ | ✅ | **PASS** |
| Levered FCF | ✅ | ✅ | ✅ | **PASS** |
| Owner Earnings | ✅ | ✅ | ⚠️ | **PASS** |
| FCFF | ✅ | ✅ | ✅ | **PASS** |

**Overall Validation Status:** ✅ **PASS**

---

## 2. Formula Verification

### 2.1 Simple FCF

**Expected Formula:** `FCF = Operating Cash Flow - Capital Expenditures`

**Code Implementation:**
```python
fcf = self.ocf - self.capex
```

**Verification:** ✅ Correct

### 2.2 Levered FCF

**Expected Formula:** `LFCF = Operating Cash Flow - CapEx - Interest Expense`

**Code Implementation:**
```python
fcf = self.ocf - self.capex - self.interest
```

**Verification:** ✅ Correct

### 2.3 Owner Earnings (Buffett Method)

**Expected Formula:** `OE = Net Income + D&A - CapEx - ΔWorking Capital`

**Code Implementation:**
```python
d_and_a = self.depreciation + self.amortization
fcf = self.net_income + d_and_a - self.capex - self.wc_change
```

**Verification:** ✅ Correct
- Note: Handles D&A as sum of depreciation and amortization ✅
- Working capital change sign: Increase in WC = cash outflow ✅

### 2.4 FCFF (Free Cash Flow to Firm)

**Expected Formula:** `FCFF = EBIT × (1 - Tax Rate) + D&A - CapEx - ΔWC`

**Code Implementation:**
```python
nopat = self.ebit * (1 - self.tax_rate)
d_and_a = self.depreciation + self.amortization
fcf = nopat + d_and_a - self.capex - self.wc_change
```

**Verification:** ✅ Correct
- NOPAT calculation: ✅ `EBIT × (1 - T)`
- D&A handling: ✅
- CapEx sign: ✅ (stored as positive, subtracted)
- WC change sign: ✅

---

## 3. Test Case Validation

### 3.1 Test Data (AAPL-like)

| Component | Value |
|-----------|-------|
| Operating Cash Flow | $110,000,000,000 |
| Capital Expenditures | $11,000,000,000 |
| Interest Expense | $3,000,000,000 |
| Net Income | $97,000,000,000 |
| Depreciation | $11,000,000,000 |
| Amortization | $500,000,000 |
| Δ Working Capital | -$2,000,000,000 |
| EBIT | $120,000,000,000 |
| Tax Rate | 16% |

### 3.2 Expected vs Calculated Results

#### Simple FCF
```
Expected: $110B - $11B = $99,000,000,000
Module:   $99,000,000,000
Status:   ✅ MATCH
```

#### Levered FCF
```
Expected: $110B - $11B - $3B = $96,000,000,000
Module:   $96,000,000,000
Status:   ✅ MATCH
```

#### Owner Earnings
```
Expected: $97B + $11.5B - $11B - (-$2B) = $99,500,000,000
         NI + D&A - CapEx - ΔWC (increase = subtract, decrease = add)
Module:   $99,500,000,000
Status:   ✅ MATCH
```

#### FCFF
```
Expected: $120B × 0.84 + $11.5B - $11B - (-$2B) = $103,300,000,000
         EBIT(1-T) + D&A - CapEx - ΔWC
         = $100.8B + $11.5B - $11B + $2B
         = $103,300,000,000
Module:   $103,300,000,000
Status:   ✅ MATCH
```

---

## 4. Edge Case Testing

### 4.1 Missing Data Handling

| Scenario | Expected | Actual | Status |
|----------|----------|--------|--------|
| No OCF → Simple FCF | Return None | Returns None | ✅ |
| No OCF → Levered FCF | Return None | Returns None | ✅ |
| No Net Income → Owner Earnings | Return None | Returns None | ✅ |
| No EBIT → FCFF | Return None | Returns None | ✅ |
| No Tax Rate | Use 21% default | Uses 21% | ✅ |
| No Interest | Use 0 | Uses 0 | ✅ |

### 4.2 Negative Values

| Scenario | Expected Behavior | Actual | Status |
|----------|-------------------|--------|--------|
| Negative OCF | Calculate correctly | ✅ Works | ✅ |
| Negative Net Income | Calculate correctly | ✅ Works | ✅ |
| Negative Working Capital Change | Adds to FCF | ✅ Works | ✅ |
| Negative EBIT | Calculate correctly | ⚠️ Works but may give odd NOPAT | ⚠️ |

**Note:** Negative EBIT gives negative NOPAT which is mathematically correct but may need UI warning.

### 4.3 CapEx Sign Convention

The module correctly handles CapEx as an absolute value:
```python
self.capex = abs(self._get_value([...]) or 0)
```

This ensures CapEx is always subtracted regardless of input sign convention. ✅

---

## 5. Data Field Normalization

The module handles multiple field name conventions:

| Standard Field | Accepted Variations |
|----------------|---------------------|
| OCF | `operating_cash_flow`, `operatingCashflow`, `OCF` |
| CapEx | `capital_expenditures`, `capitalExpenditures`, `capex`, `CapEx` |
| Interest | `interest_expense`, `interestExpense` |
| Net Income | `net_income`, `netIncome`, `NI` |
| D&A | `depreciation`, `depreciationAndAmortization`, `D&A` |
| WC Change | `change_in_working_capital`, `changeInWorkingCapital`, `delta_wc` |
| EBIT | `ebit`, `operatingIncome`, `operating_income`, `EBIT` |

**Verification:** ✅ Handles both yfinance and SEC naming conventions.

---

## 6. FCFResult Dataclass

The result structure includes:

```python
@dataclass
class FCFResult:
    method: FCFMethod       # ✅ Enum for type safety
    value: float            # ✅ The FCF value
    components: Dict        # ✅ Breakdown for transparency
    formula: str            # ✅ Human-readable formula
    description: str        # ✅ Use case explanation
```

**Verification:** ✅ Complete and well-structured.

---

## 7. Recommendation Engine

The `get_recommended_method()` logic:

| Available Data | Recommended Method | Reason |
|----------------|-------------------|--------|
| EBIT + D&A | FCFF | Best for DCF valuation |
| NI + D&A | Owner Earnings | Good for value investing |
| OCF + Interest | Levered FCF | Shows equity cash flow |
| OCF only | Simple FCF | Basic assessment |
| Limited data | Simple FCF | Default fallback |

**Verification:** ✅ Logic is sound and prioritizes valuation use cases.

---

## 8. Integration Points

### 8.1 With DCF Model
The FCFF method is ideal for DCF:
- Capital structure neutral ✅
- Uses WACC as discount rate ✅
- Returns NOPAT component for analysis ✅

### 8.2 With Streamlit UI
Can display:
- All 4 methods side-by-side ✅
- Component breakdown ✅
- Method descriptions ✅
- Recommendation ✅

---

## 9. Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| D&A may not always separate | Minor | Combined field handled |
| WC change calculation varies | Moderate | Need consistent extraction |
| Maintenance CapEx not isolated | Minor | Document assumption |
| Stock-based comp not added back | Minor | Could be future enhancement |

---

## 10. Test File Created

Created `tests/test_fcf_calculator.py` for automated validation:

```python
# Key test cases
def test_simple_fcf():
    assert simple_result.value == pytest.approx(99_000_000_000, rel=0.01)

def test_levered_fcf():
    assert levered_result.value == pytest.approx(96_000_000_000, rel=0.01)

def test_owner_earnings():
    assert oe_result.value == pytest.approx(99_500_000_000, rel=0.01)

def test_fcff():
    assert fcff_result.value == pytest.approx(103_300_000_000, rel=0.01)
```

---

## 11. Recommendations

1. **Add UI Warning:** When EBIT is negative, display warning about negative NOPAT
2. **Stock-Based Comp:** Consider adding back to Owner Earnings in future version
3. **Maintenance CapEx:** Consider splitting growth vs maintenance CapEx
4. **Historical FCF:** Support multi-year FCF calculation for trend analysis

---

## 12. Conclusion

**TASK-E009 Validation Status: ✅ PASS**

All 4 FCF methods:
- ✅ Correctly implement standard formulas
- ✅ Handle missing data gracefully
- ✅ Accept multiple field name conventions
- ✅ Return structured results with components

The `calculations/fcf_calculator.py` module is **ready for production use**.

---

**Next Steps:**
- E008: Waiting for A003 (WACC fix)
- E010: Integration test after A003 complete

