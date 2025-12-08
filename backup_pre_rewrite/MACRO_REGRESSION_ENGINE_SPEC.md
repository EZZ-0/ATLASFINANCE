# MACRO REGRESSION ENGINE - COMPREHENSIVE SPECIFICATION

## Project Overview

Build a **professional-grade Currency/GDP Regression Analysis Engine** as a Streamlit web application. This is a standalone macroeconomic analysis tool for testing economic theories like Purchasing Power Parity (PPP), Interest Rate Parity (IRP), and Monetary Models.

---

## Core Objective

Create a robust statistical engine that:
1. Fetches macroeconomic data from free APIs (FRED, World Bank, Yahoo Finance)
2. Runs econometric regressions with proper statistical diagnostics
3. Tests classic FX/macro theories (PPP, IRP, Monetary Model)
4. Provides professional visualizations and exportable reports
5. Handles time-series properly (stationarity tests, cointegration)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit |
| **Data Processing** | Pandas, NumPy |
| **Econometrics** | statsmodels |
| **Data Sources** | fredapi, yfinance, wbgapi |
| **Visualization** | Plotly |
| **PDF Export** | ReportLab |

---

## Data Sources (All Free)

### 1. FRED (Federal Reserve Economic Data)
- **API**: `fredapi` Python package
- **Key**: Free at https://fred.stlouisfed.org/docs/api/api_key.html
- **Data Available**:
  - GDP (nominal & real): `GDP`, `GDPC1`
  - CPI/Inflation: `CPIAUCSL`
  - Interest Rates: `FEDFUNDS`, `GS10`, `GS2`
  - Money Supply: `M2SL`
  - Unemployment: `UNRATE`
  - Trade Balance: `BOPGSTB`

### 2. Yahoo Finance (Currency Pairs)
- **API**: `yfinance` Python package
- **Key**: None required
- **Data Available**:
  - Major pairs: `EURUSD=X`, `GBPUSD=X`, `USDJPY=X`, `USDCHF=X`
  - Commodity currencies: `AUDUSD=X`, `USDCAD=X`, `NZDUSD=X`
  - Emerging: `USDSAR=X`, `USDAED=X`, `USDMXN=X`
  - Historical OHLC data

### 3. World Bank
- **API**: `wbgapi` Python package
- **Key**: None required
- **Data Available**:
  - GDP for all countries
  - Inflation rates
  - Trade data
  - Demographics

---

## Economic Models to Implement

### Model 1: Purchasing Power Parity (PPP)

**Theory**: Exchange rates should equalize price levels across countries.

**Equations**:
```
Absolute PPP:  S = P_domestic / P_foreign
Relative PPP:  ΔS = π_domestic - π_foreign
```

**Regression**:
```
ΔS(t) = α + β(π_d - π_f)(t) + ε(t)

Where:
- ΔS = Change in spot exchange rate
- π_d = Domestic inflation rate
- π_f = Foreign inflation rate
- If PPP holds: α ≈ 0, β ≈ 1
```

**Tests Required**:
- Unit root tests (ADF) on all variables
- Cointegration test (Engle-Granger)
- Hypothesis test: β = 1

---

### Model 2: Uncovered Interest Rate Parity (UIP)

**Theory**: Interest rate differential should equal expected exchange rate change.

**Equation**:
```
E(ΔS) = i_d - i_f

Where:
- E(ΔS) = Expected FX change
- i_d = Domestic interest rate
- i_f = Foreign interest rate
```

**Regression**:
```
ΔS(t+1) = α + β(i_d - i_f)(t) + ε(t)

If UIP holds: α ≈ 0, β ≈ 1
```

**Known Issue**: UIP typically fails empirically ("forward premium puzzle")

---

### Model 3: Monetary Model of Exchange Rates

**Theory**: FX rates determined by relative money supplies and incomes.

**Equation**:
```
s = (m_d - m_f) - φ(y_d - y_f) + λ(i_d - i_f)

Where:
- s = log(spot rate)
- m = log(money supply)
- y = log(real GDP)
- i = interest rate
```

**Regression**:
```
s(t) = α + β₁(m_d - m_f) + β₂(y_d - y_f) + β₃(i_d - i_f) + ε(t)

Expected signs: β₁ > 0, β₂ < 0, β₃ > 0 (flexible price version)
```

---

### Model 4: Taylor Rule Differential

**Theory**: FX rates follow central bank policy differentials.

**Equation**:
```
ΔS = f(policy_rate_differential, output_gap_differential, inflation_differential)
```

---

### Model 5: GDP Growth & Currency Strength

**Theory**: Stronger GDP growth attracts capital inflows, strengthening currency.

**Regression**:
```
ΔS(t) = α + β₁(GDP_growth_d - GDP_growth_f) + β₂(rate_diff) + ε(t)
```

---

## Statistical Framework

### Pre-Regression Tests (CRITICAL)

| Test | Purpose | Python Function |
|------|---------|-----------------|
| **ADF Test** | Check if series is stationary | `statsmodels.tsa.stattools.adfuller` |
| **KPSS Test** | Alternative stationarity test | `statsmodels.tsa.stattools.kpss` |
| **Cointegration** | Long-run equilibrium exists? | `statsmodels.tsa.stattools.coint` |
| **Johansen Test** | Multi-variable cointegration | `statsmodels.tsa.vector_ar.vecm.coint_johansen` |

### Regression Diagnostics (POST-REGRESSION)

| Test | Purpose | Python Function |
|------|---------|-----------------|
| **Breusch-Pagan** | Heteroskedasticity | `statsmodels.stats.diagnostic.het_breuschpagan` |
| **Durbin-Watson** | Autocorrelation | `statsmodels.stats.stattools.durbin_watson` |
| **Ljung-Box** | Serial correlation | `statsmodels.stats.diagnostic.acorr_ljungbox` |
| **Jarque-Bera** | Normality of residuals | `scipy.stats.jarque_bera` |
| **VIF** | Multicollinearity | `statsmodels.stats.outliers_influence.variance_inflation_factor` |

### Robust Standard Errors

When diagnostics fail, use:
- **HC3** (heteroskedasticity-consistent): `model.get_robustcov_results(cov_type='HC3')`
- **HAC/Newey-West** (autocorrelation): `model.get_robustcov_results(cov_type='HAC')`

---

## Project Structure

```
macro_regression_engine/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # API key template
├── README.md                       # Setup instructions
│
├── .streamlit/
│   ├── config.toml                 # Streamlit theme config
│   └── secrets.toml                # API keys (gitignored)
│
├── data/
│   ├── __init__.py
│   ├── fred_fetcher.py             # FRED API wrapper
│   ├── fx_fetcher.py               # Yahoo Finance FX data
│   ├── worldbank_fetcher.py        # World Bank API wrapper
│   ├── data_transformer.py         # Log, diff, seasonal adjustment
│   └── cache_manager.py            # SQLite caching for API calls
│
├── models/
│   ├── __init__.py
│   ├── base_regression.py          # Abstract base class for all models
│   ├── ols_regression.py           # Standard OLS with diagnostics
│   ├── cointegration.py            # Engle-Granger, Johansen tests
│   ├── var_model.py                # Vector Autoregression
│   ├── vecm_model.py               # Vector Error Correction Model
│   ├── rolling_regression.py       # Time-varying coefficients
│   └── diagnostics.py              # All statistical tests
│
├── theories/
│   ├── __init__.py
│   ├── ppp_model.py                # Purchasing Power Parity
│   ├── uip_model.py                # Uncovered Interest Parity
│   ├── monetary_model.py           # Monetary Model of FX
│   ├── taylor_rule.py              # Taylor Rule Differential
│   └── gdp_fx_model.py             # GDP-Currency relationship
│
├── tabs/
│   ├── __init__.py
│   ├── dashboard_tab.py            # Overview/summary dashboard
│   ├── data_explorer_tab.py        # Browse and visualize raw data
│   ├── ppp_tab.py                  # PPP analysis interface
│   ├── uip_tab.py                  # UIP analysis interface
│   ├── monetary_tab.py             # Monetary model interface
│   ├── custom_regression_tab.py    # User-defined regressions
│   ├── cointegration_tab.py        # Cointegration testing
│   └── forecast_tab.py             # Out-of-sample forecasting
│
├── visualization/
│   ├── __init__.py
│   ├── time_series_plots.py        # Line charts, dual-axis
│   ├── regression_plots.py         # Scatter + fitted line, residuals
│   ├── diagnostic_plots.py         # QQ plots, ACF/PACF
│   └── comparison_plots.py         # Multi-country comparisons
│
├── export/
│   ├── __init__.py
│   ├── pdf_report.py               # Generate PDF reports
│   ├── excel_export.py             # Export to Excel
│   └── csv_export.py               # Export to CSV
│
└── utils/
    ├── __init__.py
    ├── constants.py                # FRED series IDs, currency codes
    ├── formatting.py               # Number formatting, tables
    └── validation.py               # Input validation
```

---

## UI/UX Requirements

### Theme: Professional Financial Terminal

- **Background**: Dark charcoal (#0a0a0a to #121212)
- **Accent Color**: Teal/Cyan (#00bcd4) or Blue (#3b82f6)
- **Text**: Light gray (#e0e0e0) with white highlights
- **Cards**: Glassmorphism with subtle blur
- **Font**: Monospace for data (JetBrains Mono), Sans-serif for labels (Inter)

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  MACRO REGRESSION ENGINE                           [Settings]   │
├─────────────────────────────────────────────────────────────────┤
│  [Dashboard] [Data] [PPP] [UIP] [Monetary] [Custom] [Forecast]  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SIDEBAR                    │         MAIN CONTENT              │
│  ─────────                  │         ────────────              │
│  Select Model               │         Results Display           │
│  Select Countries           │         - Regression Output       │
│  Date Range                 │         - Diagnostic Tests        │
│  Frequency (M/Q/Y)          │         - Visualizations          │
│  [Run Analysis]             │         - Interpretation          │
│                             │                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Features Checklist

### Data Layer
- [ ] FRED API integration with caching
- [ ] Yahoo Finance FX data fetcher
- [ ] World Bank API for international GDP
- [ ] Data transformation utilities (log, diff, seasonal adjust)
- [ ] Handle missing data and alignment
- [ ] Support multiple frequencies (daily, monthly, quarterly, annual)

### Analysis Layer
- [ ] OLS regression with full output
- [ ] Robust standard errors (HC3, HAC)
- [ ] Pre-regression stationarity tests
- [ ] Cointegration testing (Engle-Granger)
- [ ] Johansen test for multiple variables
- [ ] Rolling window regression
- [ ] VAR model estimation
- [ ] VECM for cointegrated series

### Theory Implementation
- [ ] PPP model (absolute and relative)
- [ ] UIP model with forward premium analysis
- [ ] Monetary model (flexible and sticky price)
- [ ] Taylor rule differential
- [ ] Custom user-defined regressions

### Diagnostics
- [ ] Heteroskedasticity tests
- [ ] Autocorrelation tests
- [ ] Normality tests
- [ ] Multicollinearity (VIF)
- [ ] Structural break tests (Chow)
- [ ] Clear pass/fail indicators with recommendations

### Visualization
- [ ] Time series plots (dual-axis for FX + macro)
- [ ] Scatter plots with regression line
- [ ] Residual plots
- [ ] ACF/PACF plots
- [ ] Rolling coefficient plots
- [ ] Forecast vs actual plots

### Export
- [ ] PDF report generation
- [ ] Excel export with multiple sheets
- [ ] CSV data export
- [ ] Regression equation in LaTeX format

---

## Sample Code Snippets

### FRED Data Fetcher

```python
from fredapi import Fred
import pandas as pd
from functools import lru_cache

class FREDFetcher:
    SERIES = {
        'gdp': 'GDP',
        'real_gdp': 'GDPC1',
        'cpi': 'CPIAUCSL',
        'fed_funds': 'FEDFUNDS',
        'unemployment': 'UNRATE',
        'm2': 'M2SL',
        '10y_treasury': 'GS10',
    }
    
    def __init__(self, api_key: str):
        self.fred = Fred(api_key=api_key)
    
    @lru_cache(maxsize=50)
    def get_series(self, series_id: str, start: str = '1990-01-01') -> pd.Series:
        return self.fred.get_series(series_id, observation_start=start).dropna()
    
    def get_inflation(self) -> pd.Series:
        cpi = self.get_series('CPIAUCSL')
        return cpi.pct_change(12) * 100  # YoY
```

### Cointegration Test

```python
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

class CointegrationAnalyzer:
    def adf_test(self, series: pd.Series) -> dict:
        result = adfuller(series.dropna(), autolag='AIC')
        return {
            'adf_statistic': result[0],
            'p_value': result[1],
            'is_stationary': result[1] < 0.05
        }
    
    def engle_granger_test(self, y: pd.Series, x: pd.Series) -> dict:
        data = pd.concat([y, x], axis=1).dropna()
        coint_stat, p_value, _ = coint(data.iloc[:, 0], data.iloc[:, 1])
        return {
            'cointegration_statistic': coint_stat,
            'p_value': p_value,
            'is_cointegrated': p_value < 0.05
        }
```

### PPP Model

```python
class PPPModel:
    def run_relative_ppp(self, fx_change: pd.Series, inflation_diff: pd.Series) -> dict:
        data = pd.concat([fx_change, inflation_diff], axis=1).dropna()
        y = data.iloc[:, 0]
        X = add_constant(data.iloc[:, 1])
        
        model = OLS(y, X).fit()
        
        return {
            'alpha': model.params.iloc[0],
            'beta': model.params.iloc[1],
            'r_squared': model.rsquared,
            'ppp_holds': abs(model.params.iloc[1] - 1) < 0.3,
            'model': model
        }
```

---

## Requirements.txt

```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
statsmodels>=0.14.0
scipy>=1.11.0
yfinance>=0.2.28
fredapi>=0.5.1
wbgapi>=1.0.12
plotly>=5.18.0
reportlab>=4.0.0
python-dotenv>=1.0.0
```

---

## API Keys Required

1. **FRED API Key** (required)
   - Get free at: https://fred.stlouisfed.org/docs/api/api_key.html
   - Store in `.streamlit/secrets.toml`:
     ```toml
     FRED_API_KEY = "your_key_here"
     ```

2. **World Bank** - No key needed
3. **Yahoo Finance** - No key needed

---

## Important Notes

### Statistical Rigor

1. **ALWAYS test for stationarity** before running regressions on time series
2. **Use cointegration** for non-stationary variables (don't just difference everything)
3. **Check diagnostics** and use robust standard errors when needed
4. **Report confidence intervals**, not just point estimates
5. **Acknowledge limitations** - no model is "100% accurate"

### Common Pitfalls to Avoid

- Running OLS on non-stationary data (spurious regression)
- Ignoring autocorrelation in residuals
- Overfitting with too many variables
- Not handling data frequency mismatches
- Forgetting to align time series properly

### Academic References

- Froot & Rogoff (1995) - PPP survey
- Meese & Rogoff (1983) - FX forecasting
- Engel & West (2005) - Exchange rate models
- Taylor (1993) - Taylor Rule

---

## Deployment

### Local Development
```bash
pip install -r requirements.txt
streamlit run app.py
```

### Streamlit Cloud
1. Push to GitHub
2. Connect repo to Streamlit Cloud
3. Add FRED_API_KEY to Streamlit secrets
4. Deploy

---

## Success Criteria

The engine is complete when it can:

1. ✅ Fetch 5+ years of FX and macro data automatically
2. ✅ Run PPP regression with proper diagnostics
3. ✅ Run UIP regression and identify forward premium puzzle
4. ✅ Test for cointegration between FX and fundamentals
5. ✅ Display professional visualizations
6. ✅ Export results to PDF/Excel
7. ✅ Handle errors gracefully with clear messages
8. ✅ Work on Streamlit Cloud deployment

---

## Contact / Questions

This specification provides a complete blueprint for building a professional macroeconomic regression engine. The AI coder should follow the structure exactly and implement all statistical tests properly.

**Priority Order for Implementation:**
1. Data fetchers (FRED, Yahoo Finance)
2. Basic OLS with diagnostics
3. PPP model (simplest theory)
4. Stationarity and cointegration tests
5. UIP and Monetary models
6. Visualization
7. Export functionality
8. UI polish

---

## Why This Engine vs Excel (Investor FAQ)

### The Question: "Why would I need this if I have Excel?"

**Short Answer:** Excel is a spreadsheet. This is an econometrics platform.

### Data Acquisition

| Task | Excel | Our Engine |
|------|-------|------------|
| Get 10 years of EURUSD data | Manual download → Copy/paste → Format | One line of code, 2 seconds |
| Update data weekly | Re-download, re-paste every time | One click auto-refresh |
| Get macro data for 5 countries | 15+ manual downloads | Single function call |

**Time saved per analysis: 2-4 hours → 30 seconds**

### Statistical Capabilities

Excel's Data Analysis Toolpak runs **basic OLS only**.

| Feature | Excel | Our Engine |
|---------|-------|------------|
| ADF Test (Stationarity) | ❌ | ✅ |
| Cointegration Test | ❌ | ✅ |
| Robust Standard Errors (HAC) | ❌ | ✅ |
| Heteroskedasticity Test | ❌ | ✅ |
| VAR/VECM Models | ❌ | ✅ |
| Rolling Regression | Manual nightmare | ✅ Built-in |

**Critical Issue:** Regressing non-stationary data in Excel produces **meaningless results** (spurious regression). Our engine prevents this mistake automatically.

### Scale & Reproducibility

| Scenario | Excel | Our Engine |
|----------|-------|------------|
| Analyze 20 currency pairs | Hours | Seconds |
| Monte Carlo (10K iterations) | Crashes | Fast |
| Share with colleague | Email 50MB file | Share URL |
| Version control | "model_FINAL_v2.xlsx" | Git history |

### When to Use What

| Use Excel If... | Use Our Engine If... |
|-----------------|----------------------|
| One-off quick calculation | Repeated, rigorous analysis |
| < 50 rows of data | 500+ observations |
| You're the only user | Team/sharing needed |
| Don't care about statistical validity | Presenting to investors/academics |

---

## Competitive Analysis

### Institutional Tools (Not Our Competitors)

| Tool | Price/Year | Notes |
|------|------------|-------|
| Bloomberg Terminal | $24,000 | Banks, hedge funds |
| Refinitiv Eikon | $12,000-22,000 | Asset managers |
| FactSet | $12,000 | Limited econometrics |
| Capital IQ | $15,000 | Weak on macro |

### Academic/Professional Econometrics

| Tool | Price | Our Advantage |
|------|-------|---------------|
| EViews 14 | $1,695 perpetual | We're FREE, web-based |
| Stata | $595-1,495/year | We're FREE, no coding |
| MATLAB | $940/year + toolboxes | We're FREE |
| R/Python | $0 | We have a UI, no coding required |

### Modern Web Platforms

| Tool | Price | Gap We Fill |
|------|-------|-------------|
| Koyfin | $39/month | NO regression, NO econometrics |
| TradingEconomics | $29-99/month | NO analytical tools |
| TradingView | $0-60/month | Zero econometrics |
| FRED | FREE | No analysis, just data |

### Our Unique Position

> *"We're the first tool that gives EViews-level analysis with TradingView-level UX at FRED-level pricing ($0 to start)."*

**One-liner:** *"The Robinhood of macroeconomic analysis — democratizing tools that used to cost $24,000/year."*

---

## Monetization Strategy

### Core Philosophy

Build for monetization from Day 1, even if launching free. **No ads** — they erode credibility and don't work for niche tools.

### Revenue Model: Freemium

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 5 analyses/day, 5-year history, view only |
| **Pro** | $15/month | Unlimited, full history, PDF/Excel export |
| **Premium** | $39/month | + API access, saved models, priority support |
| **Enterprise** | $299/month | White-label, custom models, SLA |

### Revenue Projections (Conservative)

| Metric | Month 1 | Month 6 | Month 12 |
|--------|---------|---------|----------|
| Free Users | 100 | 2,000 | 10,000 |
| Paid Users (3-5%) | 5 | 150 | 500 |
| MRR | $75 | $2,250 | $7,500 |
| ARR | - | - | $90,000 |

### Features to Gate (Build Now, Monetize Later)

```
FREE TIER                          PAID TIER
─────────────────────────────────────────────────
✅ 5 analyses per day            │ ∞ Unlimited
✅ Last 5 years of data          │ Full 20+ year history
✅ View results on screen        │ Export PDF/Excel
✅ Basic PPP/UIP models          │ VAR, VECM, Monte Carlo
❌ No saved analyses             │ Save & load models
❌ No API access                 │ Full REST API
❌ "Powered by [Brand]" badge    │ White-label option
```

### Additional Revenue Streams

| Stream | Revenue Potential | Effort |
|--------|-------------------|--------|
| **API Access** (usage-based) | $5,000-15,000/month | Medium |
| **Affiliate** (broker referrals) | $50-200/signup | Low |
| **Consulting** (analysis interpretation) | $200/hour | Low |
| **White-Label Licensing** | $5,000-20,000/year per client | High |
| **Educational Course** | $199 one-time | Medium |

### Monetization Timeline

| Phase | Timeline | Goal |
|-------|----------|------|
| **MVP Launch** | Month 1-2 | Free, collect emails & usage data |
| **Soft Paywall** | Month 3 | Add Pro tier, Stripe integration |
| **API Launch** | Month 4-5 | Developer tier |
| **Scale** | Month 6-12 | $10K MRR target |

### Technical Requirements for Monetization

Build these into the architecture from Day 1:

```python
# utils/monetization.py

class UsageLimiter:
    """Track and enforce tier limits"""
    
    TIER_LIMITS = {
        'free': {
            'analyses_per_day': 5,
            'history_years': 5,
            'models': ['ols', 'ppp', 'uip'],
            'export': False,
            'api_calls': 0
        },
        'pro': {
            'analyses_per_day': float('inf'),
            'history_years': 25,
            'models': 'all',
            'export': True,
            'api_calls': 1000
        },
        'premium': {
            'analyses_per_day': float('inf'),
            'history_years': 25,
            'models': 'all',
            'export': True,
            'api_calls': float('inf')
        }
    }
    
    def check_access(self, user_tier: str, feature: str) -> bool:
        limits = self.TIER_LIMITS.get(user_tier, self.TIER_LIMITS['free'])
        return limits.get(feature, False)
```

### Database Schema for Users (Future)

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    tier VARCHAR(20) DEFAULT 'free',
    analyses_today INT DEFAULT 0,
    last_analysis_date DATE,
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE usage_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(50),
    model_used VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

*Specification Version: 1.1*
*Created: December 2024*
*Updated: December 2024 - Added competitive analysis & monetization strategy*

ao