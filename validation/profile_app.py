"""
MILESTONE-007: Performance Profiling Script
============================================
Profiles ATLAS app performance to identify bottlenecks.

Author: EXECUTOR
Created: 2025-12-08

Usage:
    python validation/profile_app.py
"""

import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from datetime import datetime


def timer(func):
    """Decorator to time function execution."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed
    return wrapper


class PerformanceProfiler:
    """Profile ATLAS app performance."""
    
    def __init__(self):
        self.results = {}
    
    def profile_yfinance_ticker(self, ticker: str) -> dict:
        """Profile yfinance Ticker operations."""
        results = {}
        
        # Time Ticker initialization
        start = time.time()
        stock = yf.Ticker(ticker)
        results['ticker_init'] = time.time() - start
        
        # Time .info fetch
        start = time.time()
        try:
            info = stock.info
            results['info_fetch'] = time.time() - start
        except Exception as e:
            results['info_fetch'] = f"ERROR: {e}"
        
        # Time financials fetch
        start = time.time()
        try:
            financials = stock.financials
            results['financials_fetch'] = time.time() - start
        except Exception as e:
            results['financials_fetch'] = f"ERROR: {e}"
        
        # Time balance sheet fetch
        start = time.time()
        try:
            balance = stock.balance_sheet
            results['balance_sheet_fetch'] = time.time() - start
        except Exception as e:
            results['balance_sheet_fetch'] = f"ERROR: {e}"
        
        # Time cash flow fetch
        start = time.time()
        try:
            cashflow = stock.cashflow
            results['cashflow_fetch'] = time.time() - start
        except Exception as e:
            results['cashflow_fetch'] = f"ERROR: {e}"
        
        # Time institutional holders fetch
        start = time.time()
        try:
            inst = stock.institutional_holders
            results['institutional_holders'] = time.time() - start
        except Exception as e:
            results['institutional_holders'] = f"ERROR: {e}"
        
        # Time insider transactions fetch
        start = time.time()
        try:
            insider = stock.insider_transactions
            results['insider_transactions'] = time.time() - start
        except Exception as e:
            results['insider_transactions'] = f"ERROR: {e}"
        
        # Time major holders fetch
        start = time.time()
        try:
            major = stock.major_holders
            results['major_holders'] = time.time() - start
        except Exception as e:
            results['major_holders'] = f"ERROR: {e}"
        
        # Time earnings dates fetch
        start = time.time()
        try:
            earnings = stock.earnings_dates
            results['earnings_dates'] = time.time() - start
        except Exception as e:
            results['earnings_dates'] = f"ERROR: {e}"
        
        # Time recommendations fetch
        start = time.time()
        try:
            recs = stock.recommendations
            results['recommendations'] = time.time() - start
        except Exception as e:
            results['recommendations'] = f"ERROR: {e}"
        
        # Time history fetch (30 days)
        start = time.time()
        try:
            hist = stock.history(period="1mo")
            results['history_1mo'] = time.time() - start
        except Exception as e:
            results['history_1mo'] = f"ERROR: {e}"
        
        return results
    
    def profile_usa_backend(self, ticker: str) -> dict:
        """Profile usa_backend.py extraction."""
        results = {}
        
        try:
            from usa_backend import USAFinancialExtractor
            
            start = time.time()
            extractor = USAFinancialExtractor()
            results['extractor_init'] = time.time() - start
            
            start = time.time()
            data = extractor.extract(ticker)
            results['full_extraction'] = time.time() - start
            
        except Exception as e:
            results['usa_backend_error'] = str(e)
        
        return results
    
    def profile_modules(self, ticker: str) -> dict:
        """Profile individual modules."""
        results = {}
        
        # Profile insider_transactions
        try:
            start = time.time()
            from insider_transactions import get_insider_summary
            summary = get_insider_summary(ticker)
            results['insider_transactions_module'] = time.time() - start
        except Exception as e:
            results['insider_transactions_module'] = f"ERROR: {e}"
        
        # Profile institutional_ownership
        try:
            start = time.time()
            from institutional_ownership import get_ownership_summary
            summary = get_ownership_summary(ticker)
            results['institutional_ownership_module'] = time.time() - start
        except Exception as e:
            results['institutional_ownership_module'] = f"ERROR: {e}"
        
        # Profile earnings_revisions
        try:
            start = time.time()
            from earnings_revisions import get_revision_summary
            summary = get_revision_summary(ticker)
            results['earnings_revisions_module'] = time.time() - start
        except Exception as e:
            results['earnings_revisions_module'] = f"ERROR: {e}"
        
        # Profile dcf_modeling
        try:
            start = time.time()
            from dcf_modeling import DCFModel
            model = DCFModel()
            results['dcf_model_init'] = time.time() - start
        except Exception as e:
            results['dcf_model_init'] = f"ERROR: {e}"
        
        return results
    
    def profile_repeat_calls(self, ticker: str) -> dict:
        """Profile repeat calls to check if caching works."""
        results = {}
        
        # First call
        start = time.time()
        stock = yf.Ticker(ticker)
        _ = stock.info
        results['first_info_call'] = time.time() - start
        
        # Second call (should be faster if cached)
        start = time.time()
        stock2 = yf.Ticker(ticker)
        _ = stock2.info
        results['second_info_call'] = time.time() - start
        
        # Third call
        start = time.time()
        stock3 = yf.Ticker(ticker)
        _ = stock3.info
        results['third_info_call'] = time.time() - start
        
        return results
    
    def run_full_profile(self, tickers: list = None) -> dict:
        """Run complete performance profile."""
        if tickers is None:
            tickers = ['AAPL', 'MSFT', 'GOOGL']
        
        print("=" * 70)
        print("ATLAS PERFORMANCE PROFILING")
        print("=" * 70)
        print(f"Start Time: {datetime.now().isoformat()}")
        print(f"Tickers: {', '.join(tickers)}")
        print()
        
        all_results = {}
        
        for ticker in tickers:
            print(f"\n{'='*50}")
            print(f"PROFILING: {ticker}")
            print('='*50)
            
            ticker_results = {}
            
            # Profile yfinance
            print("\n[1/4] yfinance operations...")
            yf_results = self.profile_yfinance_ticker(ticker)
            ticker_results['yfinance'] = yf_results
            
            for op, duration in yf_results.items():
                if isinstance(duration, float):
                    status = "⚠️ SLOW" if duration > 2.0 else "✓"
                    print(f"  {op}: {duration:.2f}s {status}")
                else:
                    print(f"  {op}: {duration}")
            
            # Profile modules
            print("\n[2/4] Module operations...")
            mod_results = self.profile_modules(ticker)
            ticker_results['modules'] = mod_results
            
            for op, duration in mod_results.items():
                if isinstance(duration, float):
                    status = "⚠️ SLOW" if duration > 3.0 else "✓"
                    print(f"  {op}: {duration:.2f}s {status}")
                else:
                    print(f"  {op}: {duration}")
            
            # Profile repeat calls
            print("\n[3/4] Repeat call caching...")
            repeat_results = self.profile_repeat_calls(ticker)
            ticker_results['caching'] = repeat_results
            
            for op, duration in repeat_results.items():
                print(f"  {op}: {duration:.2f}s")
            
            # Profile full backend
            print("\n[4/4] Full backend extraction...")
            backend_results = self.profile_usa_backend(ticker)
            ticker_results['backend'] = backend_results
            
            for op, duration in backend_results.items():
                if isinstance(duration, float):
                    status = "⚠️ SLOW" if duration > 10.0 else "✓"
                    print(f"  {op}: {duration:.2f}s {status}")
                else:
                    print(f"  {op}: {duration}")
            
            all_results[ticker] = ticker_results
        
        return all_results
    
    def generate_report(self, results: dict) -> str:
        """Generate markdown performance report."""
        report = []
        report.append("# MILESTONE-007: Performance Profile Report\n")
        report.append(f"**Generated:** {datetime.now().isoformat()}\n")
        report.append(f"**Author:** EXECUTOR\n")
        report.append("\n---\n")
        
        # Summary
        report.append("## Executive Summary\n")
        
        bottlenecks = []
        for ticker, data in results.items():
            for category, ops in data.items():
                for op, duration in ops.items():
                    if isinstance(duration, float) and duration > 2.0:
                        bottlenecks.append((ticker, category, op, duration))
        
        if bottlenecks:
            report.append("### Top Bottlenecks (>2s)\n")
            report.append("| Ticker | Category | Operation | Time (s) |\n")
            report.append("|--------|----------|-----------|----------|\n")
            for t, c, o, d in sorted(bottlenecks, key=lambda x: -x[3])[:10]:
                report.append(f"| {t} | {c} | {o} | {d:.2f} |\n")
        else:
            report.append("No major bottlenecks found (all operations <2s).\n")
        
        report.append("\n---\n")
        
        # Detailed results
        report.append("## Detailed Results\n")
        
        for ticker, data in results.items():
            report.append(f"\n### {ticker}\n")
            
            for category, ops in data.items():
                report.append(f"\n#### {category.title()}\n")
                report.append("| Operation | Time (s) | Status |\n")
                report.append("|-----------|----------|--------|\n")
                
                for op, duration in ops.items():
                    if isinstance(duration, float):
                        status = "⚠️ SLOW" if duration > 2.0 else "✅"
                        report.append(f"| {op} | {duration:.2f} | {status} |\n")
                    else:
                        report.append(f"| {op} | ERROR | ❌ |\n")
        
        report.append("\n---\n")
        
        # Recommendations
        report.append("## Recommendations\n")
        report.append("""
1. **Caching Priority:**
   - Add `@st.cache_data(ttl=3600)` to info/financials fetches
   - Add `@st.cache_resource` for Ticker objects
   
2. **Redundant Calls:**
   - Reuse single Ticker object across all data fetches
   - Avoid recreating Ticker in each module
   
3. **Lazy Loading:**
   - Defer insider/institutional data until tab opened
   - Load charts only when expander is opened
   
4. **Batch Operations:**
   - Fetch all yfinance data in one pass, store in session_state
""")
        
        return ''.join(report)


if __name__ == "__main__":
    profiler = PerformanceProfiler()
    
    # Run profile on 3 tickers
    results = profiler.run_full_profile(['AAPL', 'MSFT', 'NVDA'])
    
    # Generate report
    report = profiler.generate_report(results)
    
    # Save report
    report_path = os.path.join(os.path.dirname(__file__), 'performance_profile.md')
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n{'='*70}")
    print(f"Report saved to: {report_path}")
    print(f"{'='*70}")

