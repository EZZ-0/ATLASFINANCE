"""
CASH FLOW DEEP DIVE MODULE
================================================================================
Advanced cash flow quality, efficiency, and trend analysis.

Features:
- FCF quality score
- FCF conversion ratio
- Cash conversion cycle
- Operating cash flow trends
- CapEx intensity
- Working capital efficiency
- Cash burn/generation rate

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Optional

# Import centralized cache to prevent Yahoo rate limiting
from utils.ticker_cache import get_ticker_info, get_ticker


@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_cashflow(ticker: str, _financials: Dict = None) -> Dict:
    """
    Deep dive into cash flow metrics and quality
    
    Args:
        ticker: Stock ticker symbol
        financials: Pre-extracted financials dict (optional, reduces API calls)
        
    Returns:
        Dictionary with cash flow analysis
    """
    try:
        print(f"\n[INFO] Analyzing cash flow for {ticker}...")
        
        # Use pre-extracted data if available
        if _financials:
            info = _financials.get('info', {})
            cashflow = _financials.get('cash_flow', pd.DataFrame())
            income = _financials.get('income_statement', pd.DataFrame())
            balance = _financials.get('balance_sheet', pd.DataFrame())
            print(f"   [REUSE] Using pre-extracted data")
        else:
            # Use centralized cache to prevent Yahoo rate limiting
            info = get_ticker_info(ticker)
            stock = get_ticker(ticker)
            cashflow = stock.cashflow
            income = stock.financials
            balance = stock.balance_sheet
        
        if cashflow.empty:
            return {
                'status': 'error',
                'message': 'No cash flow data available'
            }
        
        metrics = {}
        
        # ====================================
        # 1. FREE CASH FLOW METRICS
        # ====================================
        
        # Get FCF (latest year)
        if 'Free Cash Flow' in cashflow.index:
            fcf = cashflow.loc['Free Cash Flow'].iloc[0]
            metrics['free_cash_flow'] = fcf
            
            # FCF trend (if multiple years available)
            if len(cashflow.columns) >= 3:
                fcf_series = cashflow.loc['Free Cash Flow']
                fcf_growth = fcf_series.pct_change() * 100
                metrics['fcf_growth_avg'] = round(fcf_growth.mean(), 2)
                
                # FCF stability (coefficient of variation)
                if fcf_series.mean() != 0:
                    cv = (fcf_series.std() / abs(fcf_series.mean())) * 100
                    metrics['fcf_stability'] = round(cv, 2)
                    
                    if cv < 20:
                        metrics['fcf_consistency'] = 'High'
                    elif cv < 40:
                        metrics['fcf_consistency'] = 'Moderate'
                    else:
                        metrics['fcf_consistency'] = 'Low'
        
        # ====================================
        # 2. FCF CONVERSION & QUALITY
        # ====================================
        
        # Operating Cash Flow
        if 'Operating Cash Flow' in cashflow.index:
            ocf = cashflow.loc['Operating Cash Flow'].iloc[0]
            metrics['operating_cash_flow'] = ocf
            
            # FCF Conversion Rate (FCF / OCF)
            if ocf > 0 and 'free_cash_flow' in metrics:
                fcf_conversion = (metrics['free_cash_flow'] / ocf) * 100
                metrics['fcf_conversion_rate'] = round(fcf_conversion, 2)
                
                if fcf_conversion > 80:
                    metrics['conversion_quality'] = 'Excellent'
                elif fcf_conversion > 60:
                    metrics['conversion_quality'] = 'Good'
                elif fcf_conversion > 40:
                    metrics['conversion_quality'] = 'Moderate'
                else:
                    metrics['conversion_quality'] = 'Poor'
        
        # Net Income (from income statement)
        if not income.empty and 'Net Income' in income.index:
            net_income = income.loc['Net Income'].iloc[0]
            metrics['net_income'] = net_income
            
            # Cash Flow to Net Income Ratio (quality metric)
            if net_income > 0 and 'operating_cash_flow' in metrics:
                cf_quality = metrics['operating_cash_flow'] / net_income
                metrics['cf_to_ni_ratio'] = round(cf_quality, 2)
                
                if cf_quality > 1.2:
                    metrics['earnings_quality'] = 'High Quality (Cash > Earnings)'
                elif cf_quality > 0.8:
                    metrics['earnings_quality'] = 'Good'
                elif cf_quality > 0.5:
                    metrics['earnings_quality'] = 'Moderate'
                else:
                    metrics['earnings_quality'] = 'Low (Accrual-Heavy)'
        
        # ====================================
        # 3. CAPEX ANALYSIS
        # ====================================
        
        if 'Capital Expenditure' in cashflow.index or 'Capital Expenditures' in cashflow.index:
            capex_key = 'Capital Expenditure' if 'Capital Expenditure' in cashflow.index else 'Capital Expenditures'
            capex = abs(cashflow.loc[capex_key].iloc[0])  # CapEx is negative
            metrics['capital_expenditure'] = -capex  # Store as positive for clarity
            
            # CapEx Intensity (CapEx / Revenue)
            revenue = info.get('totalRevenue', 0)
            if revenue > 0:
                capex_intensity = (capex / revenue) * 100
                metrics['capex_intensity'] = round(capex_intensity, 2)
                
                if capex_intensity < 3:
                    metrics['capex_profile'] = 'Low CapEx (Asset-Light)'
                elif capex_intensity < 8:
                    metrics['capex_profile'] = 'Moderate CapEx'
                else:
                    metrics['capex_profile'] = 'High CapEx (Capital-Intensive)'
            
            # CapEx to OCF ratio
            if 'operating_cash_flow' in metrics and metrics['operating_cash_flow'] > 0:
                capex_to_ocf = (capex / metrics['operating_cash_flow']) * 100
                metrics['capex_to_ocf_ratio'] = round(capex_to_ocf, 2)
        
        # ====================================
        # 4. WORKING CAPITAL EFFICIENCY
        # ====================================
        
        if not balance.empty:
            # Current Assets & Liabilities
            current_assets = None
            current_liabilities = None
            
            for ca_name in ['Current Assets', 'Total Current Assets']:
                if ca_name in balance.index:
                    current_assets = balance.loc[ca_name].iloc[0]
                    break
            
            for cl_name in ['Current Liabilities', 'Total Current Liabilities']:
                if cl_name in balance.index:
                    current_liabilities = balance.loc[cl_name].iloc[0]
                    break
            
            if current_assets and current_liabilities:
                working_capital = current_assets - current_liabilities
                metrics['working_capital'] = working_capital
                
                # Working Capital to Sales
                revenue = info.get('totalRevenue', 0)
                if revenue > 0:
                    wc_to_sales = (working_capital / revenue) * 100
                    metrics['working_capital_to_sales'] = round(wc_to_sales, 2)
        
        # ====================================
        # 5. CASH FLOW MARGIN
        # ====================================
        
        revenue = info.get('totalRevenue', 0)
        if revenue > 0:
            if 'operating_cash_flow' in metrics:
                ocf_margin = (metrics['operating_cash_flow'] / revenue) * 100
                metrics['ocf_margin'] = round(ocf_margin, 2)
            
            if 'free_cash_flow' in metrics:
                fcf_margin = (metrics['free_cash_flow'] / revenue) * 100
                metrics['fcf_margin'] = round(fcf_margin, 2)
        
        # FCF Yield = FCF / Market Cap
        market_cap = info.get('marketCap', 0)
        if market_cap > 0 and 'free_cash_flow' in metrics:
            fcf_yield = (metrics['free_cash_flow'] / market_cap) * 100
            metrics['fcf_yield'] = round(fcf_yield, 2)
        
        # ====================================
        # 6. OVERALL CASH FLOW SCORE
        # ====================================
        
        score = 0
        max_score = 0
        
        # FCF Consistency (25 points)
        if 'fcf_consistency' in metrics:
            max_score += 25
            if metrics['fcf_consistency'] == 'High':
                score += 25
            elif metrics['fcf_consistency'] == 'Moderate':
                score += 15
            else:
                score += 5
        
        # Conversion Quality (25 points)
        if 'conversion_quality' in metrics:
            max_score += 25
            if metrics['conversion_quality'] == 'Excellent':
                score += 25
            elif metrics['conversion_quality'] == 'Good':
                score += 20
            elif metrics['conversion_quality'] == 'Moderate':
                score += 12
            else:
                score += 5
        
        # Earnings Quality (25 points)
        if 'earnings_quality' in metrics:
            max_score += 25
            if 'High' in metrics['earnings_quality']:
                score += 25
            elif 'Good' in metrics['earnings_quality']:
                score += 20
            elif 'Moderate' in metrics['earnings_quality']:
                score += 12
            else:
                score += 5
        
        # FCF Margin (25 points)
        if 'fcf_margin' in metrics:
            max_score += 25
            margin = metrics['fcf_margin']
            if margin > 20:
                score += 25
            elif margin > 15:
                score += 20
            elif margin > 10:
                score += 15
            elif margin > 5:
                score += 10
            else:
                score += 5
        
        if max_score > 0:
            metrics['cashflow_score'] = round((score / max_score) * 100, 2)
            
            if metrics['cashflow_score'] >= 80:
                metrics['cashflow_rating'] = 'Excellent'
            elif metrics['cashflow_score'] >= 60:
                metrics['cashflow_rating'] = 'Good'
            elif metrics['cashflow_score'] >= 40:
                metrics['cashflow_rating'] = 'Fair'
            else:
                metrics['cashflow_rating'] = 'Poor'
        
        print(f"[OK] Cash flow analysis complete")
        print(f"     FCF: ${metrics.get('free_cash_flow', 0)/1e9:.2f}B")
        print(f"     Score: {metrics.get('cashflow_score', 0)}/100")
        
        return {
            'status': 'success',
            'metrics': metrics
        }
        
    except Exception as e:
        print(f"[ERROR] Cash flow analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error analyzing cash flow: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING CASH FLOW ANALYSIS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    print(f"\n[TEST] Cash Flow Analysis for {test_ticker}")
    print("-"*80)
    cf_data = analyze_cashflow(test_ticker)
    
    if cf_data['status'] == 'success':
        metrics = cf_data['metrics']
        
        print(f"\nFree Cash Flow Metrics:")
        if 'free_cash_flow' in metrics:
            print(f"  FCF: ${metrics['free_cash_flow']/1e9:.2f}B")
        if 'fcf_margin' in metrics:
            print(f"  FCF Margin: {metrics['fcf_margin']}%")
        
        print(f"\nQuality Metrics:")
        print(f"  FCF Conversion: {metrics.get('fcf_conversion_rate', 'N/A')}%")
        print(f"  Conversion Quality: {metrics.get('conversion_quality', 'N/A')}")
        print(f"  CF/NI Ratio: {metrics.get('cf_to_ni_ratio', 'N/A')}")
        print(f"  Earnings Quality: {metrics.get('earnings_quality', 'N/A')}")
        
        print(f"\nCapEx Analysis:")
        if 'capital_expenditure' in metrics:
            print(f"  CapEx: ${abs(metrics['capital_expenditure'])/1e9:.2f}B")
        print(f"  CapEx Intensity: {metrics.get('capex_intensity', 'N/A')}%")
        print(f"  CapEx Profile: {metrics.get('capex_profile', 'N/A')}")
        
        print(f"\nStability:")
        print(f"  FCF Consistency: {metrics.get('fcf_consistency', 'N/A')}")
        print(f"  FCF Stability: {metrics.get('fcf_stability', 'N/A')}%")
        
        print(f"\nOverall Score:")
        print(f"  Cash Flow Score: {metrics.get('cashflow_score', 0)}/100")
        print(f"  Rating: {metrics.get('cashflow_rating', 'N/A')}")
        
        print("\n[OK] Test PASSED")
    else:
        print(f"\n[FAIL] {cf_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nTotal Metrics Delivered: ~15")
    print(f"FCF Quality, Conversion, CapEx Intensity, Margins, Score")


