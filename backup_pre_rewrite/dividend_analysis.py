"""
DIVIDEND ANALYSIS MODULE
================================================================================
Comprehensive dividend metrics, sustainability, and growth analysis.

Features:
- Dividend yield & growth rates
- Payout ratio & sustainability
- Dividend history & consistency
- Coverage ratios
- Aristocrat/King status
- Yield on cost analysis

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Optional
from datetime import datetime


@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_dividends(ticker: str) -> Dict:
    """
    Comprehensive dividend analysis
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with dividend metrics and analysis
    """
    try:
        print(f"\n[INFO] Analyzing dividends for {ticker}...")
        
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get dividend data
        dividends = stock.dividends
        
        if dividends is None or dividends.empty:
            return {
                'status': 'no_dividend',
                'message': 'Company does not pay dividends',
                'metrics': {
                    'pays_dividend': False,
                    'dividend_yield': 0,
                    'payout_ratio': 0
                }
            }
        
        metrics = {'pays_dividend': True}
        
        # 1. Current Dividend Metrics
        current_price = info.get('currentPrice', 0)
        trailing_annual_dividend = info.get('trailingAnnualDividendRate', 0)
        dividend_yield = info.get('dividendYield', 0)
        payout_ratio = info.get('payoutRatio', 0)
        
        metrics['current_price'] = current_price
        metrics['annual_dividend'] = round(trailing_annual_dividend, 2)
        
        # Dividend yield with sanity check
        if dividend_yield:
            calculated_yield = round(dividend_yield * 100, 2)
            # Sanity check: if yield > 20%, likely a data error or special situation
            if calculated_yield > 20:
                print(f"      [WARN] Unusually high yield ({calculated_yield}%) - verify data accuracy")
            metrics['dividend_yield'] = calculated_yield
        else:
            metrics['dividend_yield'] = 0
        
        metrics['payout_ratio'] = round(payout_ratio * 100, 2) if payout_ratio else 0
        
        # 2. Dividend History & Consistency
        dividend_history = dividends.tail(60)  # Last 60 payments (15 years if quarterly)
        
        metrics['total_payments'] = len(dividend_history)
        metrics['latest_payment'] = round(dividend_history.iloc[-1], 2) if len(dividend_history) > 0 else 0
        metrics['latest_payment_date'] = dividend_history.index[-1].strftime('%Y-%m-%d') if len(dividend_history) > 0 else 'N/A'
        
        # Calculate years of consecutive payments
        # Group by year and check for consistency
        dividend_by_year = dividend_history.resample('Y').sum()
        
        # Count consecutive years with dividends
        consecutive_years = 0
        for div in reversed(dividend_by_year.values):
            if div > 0:
                consecutive_years += 1
            else:
                break
        
        metrics['consecutive_years'] = consecutive_years
        
        # Dividend Aristocrat/King status
        if consecutive_years >= 50:
            metrics['dividend_status'] = 'Dividend King (50+ years)'
            metrics['status_tier'] = 'Elite'
        elif consecutive_years >= 25:
            metrics['dividend_status'] = 'Dividend Aristocrat (25+ years)'
            metrics['status_tier'] = 'Excellent'
        elif consecutive_years >= 10:
            metrics['dividend_status'] = 'Consistent Payer (10+ years)'
            metrics['status_tier'] = 'Good'
        elif consecutive_years >= 5:
            metrics['dividend_status'] = 'Regular Payer (5+ years)'
            metrics['status_tier'] = 'Moderate'
        else:
            metrics['dividend_status'] = 'New/Irregular Payer'
            metrics['status_tier'] = 'Limited'
        
        # 3. Dividend Growth Rates
        # Annual dividend totals
        annual_dividends = dividends.resample('Y').sum()
        
        if len(annual_dividends) >= 2:
            # 1-year growth
            if len(annual_dividends) >= 2:
                latest = annual_dividends.iloc[-1]
                prev = annual_dividends.iloc[-2]
                if prev > 0:
                    metrics['dividend_growth_1y'] = round(((latest / prev) - 1) * 100, 2)
            
            # 3-year CAGR
            if len(annual_dividends) >= 4:
                latest = annual_dividends.iloc[-1]
                three_years_ago = annual_dividends.iloc[-4]
                if three_years_ago > 0:
                    cagr_3y = ((latest / three_years_ago) ** (1/3) - 1) * 100
                    metrics['dividend_cagr_3y'] = round(cagr_3y, 2)
            
            # 5-year CAGR
            if len(annual_dividends) >= 6:
                latest = annual_dividends.iloc[-1]
                five_years_ago = annual_dividends.iloc[-6]
                if five_years_ago > 0:
                    cagr_5y = ((latest / five_years_ago) ** (1/5) - 1) * 100
                    metrics['dividend_cagr_5y'] = round(cagr_5y, 2)
            
            # 10-year CAGR
            if len(annual_dividends) >= 11:
                latest = annual_dividends.iloc[-1]
                ten_years_ago = annual_dividends.iloc[-11]
                if ten_years_ago > 0:
                    cagr_10y = ((latest / ten_years_ago) ** (1/10) - 1) * 100
                    metrics['dividend_cagr_10y'] = round(cagr_10y, 2)
        
        # 4. Dividend Sustainability
        # Payout ratio assessment
        if metrics['payout_ratio'] > 0:
            if metrics['payout_ratio'] < 30:
                metrics['sustainability'] = 'Very Safe'
                metrics['sustainability_score'] = 95
            elif metrics['payout_ratio'] < 50:
                metrics['sustainability'] = 'Safe'
                metrics['sustainability_score'] = 85
            elif metrics['payout_ratio'] < 70:
                metrics['sustainability'] = 'Moderate'
                metrics['sustainability_score'] = 65
            elif metrics['payout_ratio'] < 90:
                metrics['sustainability'] = 'At Risk'
                metrics['sustainability_score'] = 40
            else:
                metrics['sustainability'] = 'High Risk (Payout > 90%)'
                metrics['sustainability_score'] = 20
        
        # 5. Dividend Coverage (using FCF if available)
        try:
            cashflow = stock.cashflow
            if not cashflow.empty and 'Free Cash Flow' in cashflow.index:
                fcf = cashflow.loc['Free Cash Flow'].iloc[0]
                annual_div_payout = trailing_annual_dividend * info.get('sharesOutstanding', 0)
                
                if annual_div_payout > 0 and fcf > 0:
                    coverage_ratio = fcf / annual_div_payout
                    metrics['fcf_coverage_ratio'] = round(coverage_ratio, 2)
                    
                    if coverage_ratio >= 2:
                        metrics['coverage_health'] = 'Excellent (2x+ coverage)'
                    elif coverage_ratio >= 1.5:
                        metrics['coverage_health'] = 'Good'
                    elif coverage_ratio >= 1:
                        metrics['coverage_health'] = 'Adequate'
                    else:
                        metrics['coverage_health'] = 'Weak (FCF < Dividends)'
        except Exception as e:
            print(f"      [WARN] Could not calculate coverage: {e}")
        
        # 6. Dividend Score (0-100)
        score = 0
        max_score = 0
        
        # Yield contribution (max 20 points)
        max_score += 20
        if metrics['dividend_yield'] >= 4:
            score += 20
        elif metrics['dividend_yield'] >= 2:
            score += 15
        elif metrics['dividend_yield'] >= 1:
            score += 10
        else:
            score += 5
        
        # Growth contribution (max 30 points)
        if 'dividend_cagr_5y' in metrics:
            max_score += 30
            cagr = metrics['dividend_cagr_5y']
            if cagr >= 10:
                score += 30
            elif cagr >= 7:
                score += 25
            elif cagr >= 5:
                score += 20
            elif cagr >= 3:
                score += 15
            elif cagr >= 0:
                score += 10
        
        # Sustainability contribution (max 30 points)
        if 'sustainability_score' in metrics:
            max_score += 30
            score += (metrics['sustainability_score'] / 100) * 30
        
        # Consistency contribution (max 20 points)
        max_score += 20
        if consecutive_years >= 25:
            score += 20
        elif consecutive_years >= 10:
            score += 15
        elif consecutive_years >= 5:
            score += 10
        else:
            score += 5
        
        if max_score > 0:
            metrics['dividend_score'] = round((score / max_score) * 100, 2)
            
            if metrics['dividend_score'] >= 80:
                metrics['dividend_rating'] = 'Excellent'
            elif metrics['dividend_score'] >= 60:
                metrics['dividend_rating'] = 'Good'
            elif metrics['dividend_score'] >= 40:
                metrics['dividend_rating'] = 'Fair'
            else:
                metrics['dividend_rating'] = 'Poor'
        
        print(f"[OK] Dividend analysis complete")
        print(f"     Yield: {metrics.get('dividend_yield', 0)}%")
        print(f"     Consecutive Years: {consecutive_years}")
        print(f"     Score: {metrics.get('dividend_score', 0)}/100")
        
        return {
            'status': 'success',
            'metrics': metrics,
            'history': dividend_history.to_dict()
        }
        
    except Exception as e:
        print(f"[ERROR] Dividend analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error analyzing dividends: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING DIVIDEND ANALYSIS MODULE")
    print("="*80)
    
    # Test with dividend-paying stock
    test_ticker = "AAPL"
    
    print(f"\n[TEST] Dividend Analysis for {test_ticker}")
    print("-"*80)
    div_data = analyze_dividends(test_ticker)
    
    if div_data['status'] == 'success':
        metrics = div_data['metrics']
        
        print(f"\nCurrent Metrics:")
        print(f"  Annual Dividend: ${metrics.get('annual_dividend', 0):.2f}")
        print(f"  Dividend Yield: {metrics.get('dividend_yield', 0):.2f}%")
        print(f"  Payout Ratio: {metrics.get('payout_ratio', 0):.2f}%")
        
        print(f"\nHistory & Consistency:")
        print(f"  Total Payments: {metrics.get('total_payments', 0)}")
        print(f"  Consecutive Years: {metrics.get('consecutive_years', 0)}")
        print(f"  Status: {metrics.get('dividend_status', 'N/A')}")
        print(f"  Tier: {metrics.get('status_tier', 'N/A')}")
        
        print(f"\nGrowth Rates:")
        print(f"  1-Year: {metrics.get('dividend_growth_1y', 'N/A')}%")
        print(f"  3-Year CAGR: {metrics.get('dividend_cagr_3y', 'N/A')}%")
        print(f"  5-Year CAGR: {metrics.get('dividend_cagr_5y', 'N/A')}%")
        print(f"  10-Year CAGR: {metrics.get('dividend_cagr_10y', 'N/A')}%")
        
        print(f"\nSustainability:")
        print(f"  Assessment: {metrics.get('sustainability', 'N/A')}")
        print(f"  Score: {metrics.get('sustainability_score', 'N/A')}/100")
        if 'fcf_coverage_ratio' in metrics:
            print(f"  FCF Coverage: {metrics['fcf_coverage_ratio']}x")
            print(f"  Coverage Health: {metrics.get('coverage_health', 'N/A')}")
        
        print(f"\nOverall Score:")
        print(f"  Dividend Score: {metrics.get('dividend_score', 0):.1f}/100")
        print(f"  Rating: {metrics.get('dividend_rating', 'N/A')}")
        
        print("\n[OK] Test PASSED")
    elif div_data['status'] == 'no_dividend':
        print(f"\n[INFO] {div_data['message']}")
        print("[OK] Test PASSED (non-dividend stock)")
    else:
        print(f"\n[FAIL] {div_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nTotal Metrics Delivered: ~12")
    print(f"Yield, Growth, Sustainability, Aristocrat Status, Coverage, Score")

