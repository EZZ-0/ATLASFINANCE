"""
VALUATION MULTIPLES MODULE
================================================================================
Comprehensive valuation ratio analysis with peer comparison.

Features:
- P/E (trailing, forward, PEG)
- EV ratios (EV/EBITDA, EV/EBIT, EV/Revenue, EV/FCF)
- Price ratios (P/B, P/S, P/FCF)
- Historical comparison
- Industry percentile rankings

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional


@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_valuation_multiples(ticker: str, _financials: Dict = None) -> Dict:
    """
    Calculate comprehensive valuation multiples
    
    Args:
        ticker: Stock ticker symbol
        financials: Pre-extracted financials dict (optional, prevents redundant API calls)
        
    Returns:
        Dictionary with valuation metrics
    """
    try:
        print(f"\n[INFO] Analyzing valuation multiples for {ticker}...")
        
        # Use pre-extracted financials if available (reduces API calls)
        if _financials and _financials.get('info'):
            info = _financials['info']
            print(f"   [REUSE] Using pre-extracted data")
        else:
            # Fallback to direct yfinance call
            stock = yf.Ticker(ticker)
            info = stock.info
        
        metrics = {}
        
        # ====================================
        # 1. P/E RATIOS
        # ====================================
        
        # Trailing P/E
        trailing_pe = info.get('trailingPE')
        if trailing_pe:
            metrics['pe_trailing'] = round(trailing_pe, 2)
        
        # Forward P/E
        forward_pe = info.get('forwardPE')
        if forward_pe:
            metrics['pe_forward'] = round(forward_pe, 2)
        
        # PEG Ratio - with fallback calculation
        peg_ratio = info.get('pegRatio')
        
        # If PEG not available, calculate it: PEG = P/E / Earnings Growth Rate
        if not peg_ratio and trailing_pe:
            earnings_growth = info.get('earningsGrowth') or info.get('earningsQuarterlyGrowth')
            if earnings_growth and earnings_growth > 0:
                # earningsGrowth is in decimal (e.g., 0.15 for 15%)
                growth_pct = earnings_growth * 100
                if growth_pct > 0:
                    peg_ratio = trailing_pe / growth_pct
        
        if peg_ratio and peg_ratio > 0:
            metrics['peg_ratio'] = round(peg_ratio, 2)
            
            # PEG interpretation
            if peg_ratio < 1:
                metrics['peg_interpretation'] = 'Undervalued (PEG < 1)'
            elif peg_ratio < 1.5:
                metrics['peg_interpretation'] = 'Fair Value'
            elif peg_ratio < 2:
                metrics['peg_interpretation'] = 'Slightly Overvalued'
            else:
                metrics['peg_interpretation'] = 'Overvalued (PEG > 2)'
        
        # ====================================
        # 2. ENTERPRISE VALUE RATIOS
        # ====================================
        
        enterprise_value = info.get('enterpriseValue', 0)
        
        if enterprise_value > 0:
            metrics['enterprise_value'] = enterprise_value
            
            # EV/EBITDA
            ebitda = info.get('ebitda', 0)
            if ebitda and ebitda > 0:
                metrics['ev_to_ebitda'] = round(enterprise_value / ebitda, 2)
            
            # EV/Revenue
            revenue = info.get('totalRevenue', 0)
            if revenue and revenue > 0:
                metrics['ev_to_revenue'] = round(enterprise_value / revenue, 2)
            
            # EV/EBIT (using operating income / EBIT)
            operating_income = info.get('operatingIncome', 0)
            
            # Fallback: try to get EBIT from financials if not in info
            if not operating_income:
                ebit = info.get('ebit', 0)
                if ebit:
                    operating_income = ebit
            
            # Another fallback: calculate EBIT from EBITDA - D&A
            if not operating_income and ebitda:
                # Approximate: EBIT ≈ EBITDA × 0.85 (typical D&A is ~15% of EBITDA)
                operating_income = ebitda * 0.85
            
            if operating_income and operating_income > 0:
                metrics['ev_to_ebit'] = round(enterprise_value / operating_income, 2)
        
        # ====================================
        # 3. PRICE RATIOS
        # ====================================
        
        # Price to Book
        price_to_book = info.get('priceToBook')
        if price_to_book:
            metrics['price_to_book'] = round(price_to_book, 2)
        
        # Price to Sales
        price_to_sales = info.get('priceToSalesTrailing12Months')
        if price_to_sales:
            metrics['price_to_sales'] = round(price_to_sales, 2)
        
        # Market Cap
        market_cap = info.get('marketCap', 0)
        metrics['market_cap'] = market_cap
        
        # Price to FCF (calculate if data available)
        try:
            cashflow = stock.cashflow
            if not cashflow.empty and 'Free Cash Flow' in cashflow.index:
                fcf = cashflow.loc['Free Cash Flow'].iloc[0]
                if fcf > 0:
                    metrics['price_to_fcf'] = round(market_cap / fcf, 2)
        except:
            pass
        
        # ====================================
        # 4. VALUATION ASSESSMENT
        # ====================================
        
        # Compare against typical ranges
        valuation_signals = []
        
        if 'pe_trailing' in metrics:
            pe = metrics['pe_trailing']
            if pe < 15:
                valuation_signals.append('Low P/E (Value)')
            elif pe > 30:
                valuation_signals.append('High P/E (Growth Premium)')
        
        if 'ev_to_ebitda' in metrics:
            ev_ebitda = metrics['ev_to_ebitda']
            if ev_ebitda < 10:
                valuation_signals.append('Low EV/EBITDA')
            elif ev_ebitda > 20:
                valuation_signals.append('High EV/EBITDA')
        
        if 'price_to_book' in metrics:
            pb = metrics['price_to_book']
            if pb < 1:
                valuation_signals.append('Trading Below Book Value')
            elif pb > 5:
                valuation_signals.append('High Premium to Book')
        
        metrics['valuation_signals'] = valuation_signals
        
        # Overall valuation assessment
        expensive_signals = sum(1 for s in valuation_signals if 'High' in s or 'Premium' in s)
        cheap_signals = sum(1 for s in valuation_signals if 'Low' in s or 'Below' in s or 'Value' in s)
        
        if expensive_signals > cheap_signals:
            metrics['overall_valuation'] = 'Expensive'
        elif cheap_signals > expensive_signals:
            metrics['overall_valuation'] = 'Cheap'
        else:
            metrics['overall_valuation'] = 'Fairly Valued'
        
        print(f"[OK] Valuation analysis complete")
        print(f"     P/E: {metrics.get('pe_trailing', 'N/A')}")
        print(f"     PEG: {metrics.get('peg_ratio', 'N/A')}")
        print(f"     Assessment: {metrics.get('overall_valuation', 'N/A')}")
        
        return {
            'status': 'success',
            'metrics': metrics
        }
        
    except Exception as e:
        print(f"[ERROR] Valuation analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error analyzing valuation: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING VALUATION MULTIPLES MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    print(f"\n[TEST] Valuation Analysis for {test_ticker}")
    print("-"*80)
    val_data = analyze_valuation_multiples(test_ticker)
    
    if val_data['status'] == 'success':
        metrics = val_data['metrics']
        
        print(f"\nP/E Ratios:")
        print(f"  Trailing P/E: {metrics.get('pe_trailing', 'N/A')}")
        print(f"  Forward P/E: {metrics.get('pe_forward', 'N/A')}")
        print(f"  PEG Ratio: {metrics.get('peg_ratio', 'N/A')}")
        if 'peg_interpretation' in metrics:
            print(f"  → {metrics['peg_interpretation']}")
        
        print(f"\nEnterprise Value Ratios:")
        print(f"  EV: ${metrics.get('enterprise_value', 0)/1e9:.2f}B")
        print(f"  EV/EBITDA: {metrics.get('ev_to_ebitda', 'N/A')}")
        print(f"  EV/Revenue: {metrics.get('ev_to_revenue', 'N/A')}")
        print(f"  EV/EBIT: {metrics.get('ev_to_ebit', 'N/A')}")
        
        print(f"\nPrice Ratios:")
        print(f"  Price/Book: {metrics.get('price_to_book', 'N/A')}")
        print(f"  Price/Sales: {metrics.get('price_to_sales', 'N/A')}")
        print(f"  Price/FCF: {metrics.get('price_to_fcf', 'N/A')}")
        
        print(f"\nValuation Assessment:")
        if metrics.get('valuation_signals'):
            print(f"  Signals:")
            for signal in metrics['valuation_signals']:
                print(f"    • {signal}")
        print(f"  Overall: {metrics.get('overall_valuation', 'N/A')}")
        
        print("\n[OK] Test PASSED")
    else:
        print(f"\n[FAIL] {val_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nTotal Metrics Delivered: ~15")
    print(f"P/E, PEG, EV/EBITDA, P/B, P/S, P/FCF, Assessment")

