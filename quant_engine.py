"""
QUANTITATIVE FINANCE ENGINE - FAMA-FRENCH 3-FACTOR MODEL
==========================================================
Advanced risk-return analysis using academic finance models.

Features:
- Historical stock prices back to 1990
- IPO date detection with smart resampling
- Fama-French 3-Factor regression for Cost of Equity
- Alpha, Beta (Market, SMB, HML) calculation
- Risk premiums and required returns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Required imports
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("[!] yfinance not installed. Install with: pip install yfinance")

try:
    import pandas_datareader as pdr
    from pandas_datareader import data as web
    DATAREADER_AVAILABLE = True
except ImportError:
    DATAREADER_AVAILABLE = False
    print("[!] pandas-datareader not installed. Install with: pip install pandas-datareader")

# Import centralized cache to prevent Yahoo rate limiting
try:
    from utils.ticker_cache import get_ticker
    TICKER_CACHE_AVAILABLE = True
except ImportError:
    TICKER_CACHE_AVAILABLE = False

# ==========================================
# FAMA-FRENCH HISTORICAL FALLBACK VALUES
# ==========================================
# Used when Kenneth French Data Library is unavailable
# Source: Historical averages 1926-2024 from French's website
# Last Updated: November 2025

FAMA_FRENCH_FALLBACK = {
    'market_premium_monthly': 0.0055,  # 6.6% annual → 0.55% monthly
    'smb_premium_monthly': 0.0017,     # 2.0% annual → 0.17% monthly
    'hml_premium_monthly': 0.0025,     # 3.0% annual → 0.25% monthly
    'risk_free_monthly': 0.0033,       # 4.0% annual → 0.33% monthly
    'source': 'Historical averages (1926-2024)',
    'note': 'Using fallback values - live data unavailable'
}

try:
    import statsmodels.api as sm
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("[!] statsmodels not installed. Install with: pip install statsmodels")


class QuantEngine:
    """
    Quantitative Analysis Engine using Fama-French 3-Factor Model
    
    Calculates:
    - Cost of Equity (not simple CAPM, but Fama-French)
    - Alpha (excess return not explained by factors)
    - Beta_Market (systematic risk)
    - Beta_SMB (size factor exposure)
    - Beta_HML (value factor exposure)
    - Risk premiums and required returns
    """
    
    def __init__(self):
        """Initialize Quant Engine"""
        self.ff_data = None  # Fama-French factor data
        self.stock_data = None  # Historical stock prices
        self.monthly_returns = None  # Monthly stock returns
        self.regression_results = None  # OLS results
    
    # ==========================================
    # 1. HISTORICAL PRICE DATA EXTRACTION
    # ==========================================
    
    def fetch_stock_history(self, ticker: str, start_date: str = "1990-01-01") -> Tuple[pd.DataFrame, str]:
        """
        Fetch historical stock prices with maximum available history.
        
        Args:
            ticker: Stock symbol
            start_date: Earliest date to attempt (default: Jan 1, 1990)
            
        Returns:
            (DataFrame with OHLCV data, IPO date string)
        """
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance required. Install with: pip install yfinance")
        
        print(f"\n[DATA] Fetching historical prices for {ticker}...")
        print(f"   Attempting to retrieve data from {start_date} to present...")
        
        try:
            # Download maximum available history (use cache if available)
            if TICKER_CACHE_AVAILABLE:
                stock = get_ticker(ticker)
            else:
                stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=datetime.today())
            
            if hist.empty:
                raise ValueError(f"No price history available for {ticker}")
            
            # Detect IPO date (first available trading date)
            ipo_date = hist.index[0].strftime("%Y-%m-%d")
            total_days = len(hist)
            years = (hist.index[-1] - hist.index[0]).days / 365.25
            
            print(f"[OK] Retrieved {total_days:,} trading days ({years:.1f} years)")
            print(f"   IPO Date (First Trading): {ipo_date}")
            print(f"   Latest Date: {hist.index[-1].strftime('%Y-%m-%d')}")
            
            self.stock_data = hist
            return hist, ipo_date
            
        except Exception as e:
            print(f"[FAIL] Failed to fetch stock history: {e}")
            return pd.DataFrame(), None
    
    def resample_by_ipo_date(self, hist: pd.DataFrame, ipo_date: str) -> Tuple[pd.DataFrame, str]:
        """
        Smart resampling based on IPO date:
        - Before 2005: Monthly intervals (long history)
        - After 2005: Weekly intervals (recent history, higher granularity)
        
        Args:
            hist: Historical price DataFrame
            ipo_date: IPO date string (YYYY-MM-DD)
            
        Returns:
            (Resampled DataFrame, resampling frequency string)
        """
        if hist.empty:
            return hist, "None"
        
        # Convert IPO date to datetime
        ipo_dt = pd.to_datetime(ipo_date)
        cutoff_date = pd.to_datetime("2005-01-01")
        
        # Determine resampling frequency
        if ipo_dt < cutoff_date:
            freq = "MS"  # Month Start
            freq_label = "Monthly"
            print(f"\n[DATE] IPO before 2005 - Resampling to MONTHLY intervals")
        else:
            freq = "W-FRI"  # Weekly (Friday)
            freq_label = "Weekly"
            print(f"\n[DATE] IPO after 2005 - Resampling to WEEKLY intervals")
        
        # Resample: Use last price of period
        resampled = hist.resample(freq).agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()
        
        print(f"   Original: {len(hist):,} daily observations")
        print(f"   Resampled: {len(resampled):,} {freq_label.lower()} observations")
        
        return resampled, freq_label
    
    def calculate_returns(self, prices: pd.DataFrame, freq: str = "Monthly") -> pd.Series:
        """
        Calculate returns from price data.
        
        Args:
            prices: DataFrame with 'Close' column
            freq: Frequency label for logging
            
        Returns:
            Series of returns
        """
        if 'Close' not in prices.columns or prices.empty:
            return pd.Series()
        
        # Calculate log returns (more stable for regression)
        returns = np.log(prices['Close'] / prices['Close'].shift(1)).dropna()
        
        print(f"\n[CALC] Calculated {len(returns)} {freq} returns")
        print(f"   Mean Return: {returns.mean()*100:.2f}%")
        print(f"   Std Dev: {returns.std()*100:.2f}%")
        print(f"   Sharpe Ratio (approx): {(returns.mean() / returns.std()) * np.sqrt(12 if freq == 'Monthly' else 52):.2f}")
        
        return returns
    
    # ==========================================
    # 2. FAMA-FRENCH FACTOR DATA
    # ==========================================
    
    def fetch_fama_french_factors(self, start_date: str = "1990-01-01") -> pd.DataFrame:
        """
        Fetch Fama-French 3-Factor data from Kenneth French's Data Library.
        
        **FALLBACK MECHANISM:**
        If live data fetch fails, uses historical averages (1926-2024):
        - Market Premium: 6.6% annual
        - SMB (Size): 2.0% annual
        - HML (Value): 3.0% annual
        - Risk-Free: 4.0% annual
        
        Factors:
        - Mkt-RF: Market excess return (market return - risk-free rate)
        - SMB: Small Minus Big (size factor)
        - HML: High Minus Low (value factor)
        - RF: Risk-free rate
        
        Args:
            start_date: Start date for factor data
            
        Returns:
            DataFrame with factors (or fallback values)
        """
        if not DATAREADER_AVAILABLE:
            print("[WARN] pandas-datareader not available. Using fallback values.")
            return self._create_fallback_factors(start_date)
        
        print(f"\n[FF-DATA] Fetching Fama-French 3-Factor data from Kenneth French Data Library...")
        
        try:
            # Fetch from Kenneth French's website
            ff_data = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start=start_date)[0]
            
            # Data comes in percentage points, convert to decimals
            ff_data = ff_data / 100
            
            print(f"[OK] Retrieved {len(ff_data)} monthly observations")
            print(f"   Date Range: {ff_data.index[0]} to {ff_data.index[-1]}")
            print(f"   Factors: {', '.join(ff_data.columns.tolist())}")
            
            # Display sample statistics
            print(f"\n   Factor Statistics (annualized):")
            print(f"   Mkt-RF Mean: {ff_data['Mkt-RF'].mean()*12*100:.2f}%")
            print(f"   SMB Mean: {ff_data['SMB'].mean()*12*100:.2f}%")
            print(f"   HML Mean: {ff_data['HML'].mean()*12*100:.2f}%")
            print(f"   RF Mean: {ff_data['RF'].mean()*12*100:.2f}%")
            
            self.ff_data = ff_data
            return ff_data
            
        except Exception as e:
            print(f"[FAIL] Failed to fetch Fama-French data: {e}")
            print("   Using fallback historical averages instead...")
            return self._create_fallback_factors(start_date)
    
    def _create_fallback_factors(self, start_date: str = "1990-01-01") -> pd.DataFrame:
        """
        Create synthetic Fama-French factors using historical averages.
        Used as fallback when live data is unavailable.
        
        Returns:
            DataFrame with fallback factor values
        """
        print(f"\n[FALLBACK] Creating synthetic Fama-French factors...")
        print(f"   Using historical averages (1926-2024):")
        print(f"   - Market Premium: 6.6% annual")
        print(f"   - SMB (Size): 2.0% annual")
        print(f"   - HML (Value): 3.0% annual")
        print(f"   - Risk-Free: 4.0% annual")
        
        # Create a monthly date range from start_date to present
        start = pd.to_datetime(start_date)
        end = pd.Timestamp.today()
        date_range = pd.date_range(start=start, end=end, freq='MS')  # Month Start
        
        # Create DataFrame with fallback values
        fallback_df = pd.DataFrame({
            'Mkt-RF': FAMA_FRENCH_FALLBACK['market_premium_monthly'],
            'SMB': FAMA_FRENCH_FALLBACK['smb_premium_monthly'],
            'HML': FAMA_FRENCH_FALLBACK['hml_premium_monthly'],
            'RF': FAMA_FRENCH_FALLBACK['risk_free_monthly']
        }, index=date_range)
        
        print(f"[OK] Generated {len(fallback_df)} monthly observations")
        print(f"   Date Range: {fallback_df.index[0].strftime('%Y-%m')} to {fallback_df.index[-1].strftime('%Y-%m')}")
        print(f"   ⚠️  Note: Using fixed historical averages, not live data")
        
        return fallback_df
    
    # ==========================================
    # 3. FAMA-FRENCH REGRESSION
    # ==========================================
    
    def run_fama_french_regression(self, ticker: str, stock_returns: pd.Series, 
                                   ff_data: pd.DataFrame) -> Dict:
        """
        Run OLS regression using Fama-French 3-Factor Model.
        
        Model: R_i - R_f = a + b_Mkt(R_Mkt - R_f) + b_SMB(SMB) + b_HML(HML) + e
        
        Where:
        - R_i: Stock return
        - R_f: Risk-free rate
        - R_Mkt: Market return
        - SMB: Size factor
        - HML: Value factor
        - a (Alpha): Excess return not explained by factors
        - b: Factor loadings (sensitivities)
        
        Args:
            ticker: Stock symbol
            stock_returns: Series of stock returns
            ff_data: Fama-French factor DataFrame
            
        Returns:
            Dictionary with regression results
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels required. Install with: pip install statsmodels")
        
        print(f"\n[REGRESSION] Running Fama-French 3-Factor Regression for {ticker}...")
        
        try:
            # Align stock returns with Fama-French data (both should be monthly)
            # Convert stock_returns index to period for matching
            stock_returns_monthly = stock_returns.copy()
            stock_returns_monthly.index = pd.to_datetime(stock_returns_monthly.index).to_period('M')
            
            # Merge
            merged = pd.DataFrame({
                'Stock_Return': stock_returns_monthly
            }).join(ff_data, how='inner')
            
            # Drop any NaN values
            merged = merged.dropna()
            
            if len(merged) < 24:
                print(f"[WARN] Warning: Only {len(merged)} observations. Need at least 24 for reliable results.")
            
            print(f"   Aligned {len(merged)} monthly observations for regression")
            
            # Calculate excess return (R_i - R_f)
            merged['Excess_Return'] = merged['Stock_Return'] - merged['RF']
            
            # Prepare regression variables
            Y = merged['Excess_Return']  # Dependent variable
            X = merged[['Mkt-RF', 'SMB', 'HML']]  # Independent variables
            X = sm.add_constant(X)  # Add intercept
            
            # Run OLS regression
            model = sm.OLS(Y, X).fit()
            
            # Extract results
            alpha = model.params['const']
            beta_market = model.params['Mkt-RF']
            beta_smb = model.params['SMB']
            beta_hml = model.params['HML']
            
            # Statistical significance
            p_alpha = model.pvalues['const']
            p_market = model.pvalues['Mkt-RF']
            p_smb = model.pvalues['SMB']
            p_hml = model.pvalues['HML']
            
            # Model fit
            r_squared = model.rsquared
            adj_r_squared = model.rsquared_adj
            
            # Calculate Cost of Equity using Fama-French
            # E(R_i) = R_f + β_Mkt*E(Mkt-RF) + β_SMB*E(SMB) + β_HML*E(HML)
            avg_rf = ff_data['RF'].mean()
            avg_mkt_premium = ff_data['Mkt-RF'].mean()
            avg_smb = ff_data['SMB'].mean()
            avg_hml = ff_data['HML'].mean()
            
            cost_of_equity_monthly = avg_rf + (beta_market * avg_mkt_premium) + (beta_smb * avg_smb) + (beta_hml * avg_hml)
            cost_of_equity_annual = (1 + cost_of_equity_monthly) ** 12 - 1
            
            # Display results
            print(f"\n{'='*60}")
            print(f"  FAMA-FRENCH 3-FACTOR REGRESSION RESULTS")
            print(f"{'='*60}")
            print(f"Alpha (a):           {alpha*100:.4f}% monthly ({alpha*12*100:.2f}% annualized)")
            print(f"  - Significance:    {'***' if p_alpha < 0.01 else '**' if p_alpha < 0.05 else '*' if p_alpha < 0.10 else 'NS'} (p={p_alpha:.4f})")
            print(f"\nBeta Market (b-Mkt):  {beta_market:.4f}")
            print(f"  - Significance:    {'***' if p_market < 0.01 else '**' if p_market < 0.05 else '*' if p_market < 0.10 else 'NS'} (p={p_market:.4f})")
            print(f"  - Interpretation:  {self._interpret_beta_market(beta_market)}")
            print(f"\nBeta SMB (b-SMB):     {beta_smb:.4f}")
            print(f"  - Significance:    {'***' if p_smb < 0.01 else '**' if p_smb < 0.05 else '*' if p_smb < 0.10 else 'NS'} (p={p_smb:.4f})")
            print(f"  - Interpretation:  {self._interpret_beta_smb(beta_smb)}")
            print(f"\nBeta HML (b-HML):     {beta_hml:.4f}")
            print(f"  - Significance:    {'***' if p_hml < 0.01 else '**' if p_hml < 0.05 else '*' if p_hml < 0.10 else 'NS'} (p={p_hml:.4f})")
            print(f"  - Interpretation:  {self._interpret_beta_hml(beta_hml)}")
            print(f"\n{'='*60}")
            print(f"R-Squared:           {r_squared:.4f}")
            print(f"Adj R-Squared:       {adj_r_squared:.4f}")
            print(f"Observations:        {len(merged)}")
            print(f"{'='*60}")
            print(f"\nCOST OF EQUITY (Fama-French):")
            print(f"  Monthly:  {cost_of_equity_monthly*100:.4f}%")
            print(f"  Annual:   {cost_of_equity_annual*100:.2f}%")
            print(f"{'='*60}\n")
            
            # Store results
            self.regression_results = model
            
            return {
                "alpha": alpha,
                "alpha_annualized": alpha * 12,
                "beta_market": beta_market,
                "beta_smb": beta_smb,
                "beta_hml": beta_hml,
                "p_values": {
                    "alpha": p_alpha,
                    "market": p_market,
                    "smb": p_smb,
                    "hml": p_hml
                },
                "r_squared": r_squared,
                "adj_r_squared": adj_r_squared,
                "observations": len(merged),
                "cost_of_equity_monthly": cost_of_equity_monthly,
                "cost_of_equity_annual": cost_of_equity_annual,
                "risk_free_rate": avg_rf,
                "market_premium": avg_mkt_premium,
                "smb_premium": avg_smb,
                "hml_premium": avg_hml,
                "model": model,
                "stock_monthly_return": stock_returns_monthly.mean(),
                "required_return_monthly": cost_of_equity_monthly,
                "required_return_annual": cost_of_equity_annual
            }
            
        except Exception as e:
            print(f"[FAIL] Regression failed: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _interpret_beta_market(self, beta: float) -> str:
        """Interpret market beta"""
        if beta > 1.2:
            return "High volatility, moves more than market"
        elif beta > 0.8:
            return "Moves with market (neutral risk)"
        elif beta > 0:
            return "Low volatility, defensive stock"
        else:
            return "Moves opposite to market (hedge)"
    
    def _interpret_beta_smb(self, beta: float) -> str:
        """Interpret SMB (size) beta"""
        if abs(beta) < 0.3:
            return "Neutral to size factor"
        elif beta > 0:
            return "Behaves like small-cap stock"
        else:
            return "Behaves like large-cap stock"
    
    def _interpret_beta_hml(self, beta: float) -> str:
        """Interpret HML (value) beta"""
        if abs(beta) < 0.3:
            return "Neutral to value factor"
        elif beta > 0:
            return "Value stock characteristics"
        else:
            return "Growth stock characteristics"
    
    # ==========================================
    # 4. COMPLETE ANALYSIS PIPELINE
    # ==========================================
    
    def analyze_stock(self, ticker: str) -> Dict:
        """
        Complete quantitative analysis for a stock.
        
        Steps:
        1. Fetch historical prices (back to 1990)
        2. Detect IPO date
        3. Resample intelligently (Monthly if IPO < 2005, Weekly if IPO >= 2005)
        4. Calculate returns
        5. Fetch Fama-French factors
        6. Resample stock returns to monthly for regression
        7. Run Fama-French 3-Factor regression
        8. Calculate Cost of Equity and all metrics
        
        Args:
            ticker: Stock symbol
            
        Returns:
            Comprehensive results dictionary
        """
        print(f"\n{'='*70}")
        print(f"  COMPREHENSIVE QUANTITATIVE ANALYSIS: {ticker.upper()}")
        print(f"{'='*70}")
        
        # Step 1: Fetch price history
        hist, ipo_date = self.fetch_stock_history(ticker)
        if hist.empty:
            return {"status": "error", "message": "No price history available"}
        
        # Step 2: Resample by IPO date
        resampled, freq = self.resample_by_ipo_date(hist, ipo_date)
        
        # Step 3: Calculate returns
        returns = self.calculate_returns(resampled, freq)
        
        # Step 4: For Fama-French, we need monthly returns
        # If we have weekly data, resample to monthly for regression
        if freq == "Weekly":
            print(f"\n[CONVERT] Resampling to MONTHLY for Fama-French regression...")
            monthly_prices = hist.resample('MS').agg({
                'Close': 'last'
            }).dropna()
            monthly_returns = self.calculate_returns(monthly_prices, "Monthly")
        else:
            monthly_returns = returns
        
        self.monthly_returns = monthly_returns
        
        # Step 5: Fetch Fama-French factors
        ff_data = self.fetch_fama_french_factors(start_date="1990-01-01")
        if ff_data.empty:
            return {"status": "error", "message": "Failed to fetch Fama-French factors"}
        
        # Step 6: Run regression
        regression_results = self.run_fama_french_regression(ticker, monthly_returns, ff_data)
        if not regression_results:
            return {"status": "error", "message": "Regression failed"}
        
        # Step 7: Compile comprehensive results
        results = {
            "status": "success",
            "ticker": ticker.upper(),
            "ipo_date": ipo_date,
            "data_frequency": freq,
            "total_observations": len(hist),
            "resampled_observations": len(resampled),
            "date_range": {
                "start": hist.index[0].strftime("%Y-%m-%d"),
                "end": hist.index[-1].strftime("%Y-%m-%d"),
                "years": (hist.index[-1] - hist.index[0]).days / 365.25
            },
            "returns": {
                "mean_return": returns.mean(),
                "std_dev": returns.std(),
                "monthly_mean": monthly_returns.mean(),
                "monthly_std": monthly_returns.std(),
                "annualized_return": (1 + returns.mean()) ** (252 if freq == "Weekly" else 12) - 1,
                "annualized_volatility": returns.std() * np.sqrt(252 if freq == "Weekly" else 12)
            },
            "fama_french": regression_results,
            "price_history": hist,
            "resampled_history": resampled,
            "returns_series": returns,
            "monthly_returns_series": monthly_returns
        }
        
        return results


# === CONVENIENCE FUNCTIONS ===

def quick_quant_analysis(ticker: str) -> Dict:
    """
    One-line function for complete quant analysis.
    
    Usage:
        results = quick_quant_analysis("AAPL")
        print(f"Cost of Equity: {results['fama_french']['cost_of_equity_annual']*100:.2f}%")
    """
    engine = QuantEngine()
    return engine.analyze_stock(ticker)

