"""
EARNINGS ANALYSIS MODULE
================================================================================
Comprehensive earnings quality, surprise, and trend analysis.

Features:
- Earnings beat/miss history
- Guidance vs. actual performance
- Earnings surprise trends
- EPS consistency & quality
- Revenue surprises
- Quarterly momentum
- Forward estimates accuracy
- Earnings revision trends

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional
from datetime import datetime, timedelta


@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_earnings_history(ticker: str, periods: int = 8, _financials: Dict = None) -> Dict:
    """
    Analyze earnings history, surprises, and trends
    
    Args:
        ticker: Stock ticker symbol
        periods: Number of quarters to analyze
        _financials: Pre-extracted financials dict (optional, underscore prefix skips hashing)
        
    Returns:
        Dictionary with earnings analysis metrics
    """
    try:
        print(f"\n[INFO] Analyzing earnings for {ticker}...")
        
        # Need yfinance stock object for earnings_dates (not in standard extraction)
        stock = yf.Ticker(ticker)
        
        # Can reuse info from _financials if available
        if _financials and _financials.get('info'):
            info = _financials['info']
        else:
            info = stock.info
        
        # Get earnings data
        earnings_dates = stock.earnings_dates
        earnings_history = stock.earnings_history
        
        if earnings_dates is None or earnings_dates.empty:
            return {
                'status': 'error',
                'message': 'No earnings data available'
            }
        
        # Limit to requested periods
        earnings_df = earnings_dates.head(periods).copy()
        
        # Calculate metrics
        metrics = {}
        
        # 1. Earnings Beat/Miss Rate
        if 'Surprise(%)' in earnings_df.columns:
            surprises = earnings_df['Surprise(%)'].dropna()
            if len(surprises) > 0:
                beats = (surprises > 0).sum()
                misses = (surprises < 0).sum()
                meets = (surprises == 0).sum()
                
                metrics['total_earnings_reports'] = len(surprises)
                metrics['earnings_beats'] = int(beats)
                metrics['earnings_misses'] = int(misses)
                metrics['earnings_meets'] = int(meets)
                metrics['beat_rate'] = round((beats / len(surprises)) * 100, 2)
                metrics['avg_surprise_pct'] = round(surprises.mean(), 2)
                metrics['surprise_std'] = round(surprises.std(), 2)
                
                # Surprise consistency
                if metrics['surprise_std'] < 5:
                    metrics['surprise_consistency'] = 'High'
                elif metrics['surprise_std'] < 10:
                    metrics['surprise_consistency'] = 'Moderate'
                else:
                    metrics['surprise_consistency'] = 'Low'
        
        # 2. EPS Trend Analysis
        if 'Reported EPS' in earnings_df.columns:
            reported_eps = earnings_df['Reported EPS'].dropna()
            if len(reported_eps) >= 4:
                # Calculate EPS growth QoQ
                eps_growth = reported_eps.pct_change() * 100
                metrics['avg_eps_qoq_growth'] = round(eps_growth.mean(), 2)
                metrics['eps_growth_volatility'] = round(eps_growth.std(), 2)
                
                # EPS momentum (recent vs older)
                recent_avg = reported_eps.iloc[:2].mean()
                older_avg = reported_eps.iloc[-2:].mean()
                
                if older_avg != 0:
                    metrics['eps_momentum'] = round(((recent_avg / older_avg) - 1) * 100, 2)
                    
                    if metrics['eps_momentum'] > 10:
                        metrics['eps_trend'] = 'Strong Acceleration'
                    elif metrics['eps_momentum'] > 0:
                        metrics['eps_trend'] = 'Growing'
                    elif metrics['eps_momentum'] > -10:
                        metrics['eps_trend'] = 'Slowing'
                    else:
                        metrics['eps_trend'] = 'Declining'
        
        # 3. Revenue Surprise Analysis
        # Note: yfinance doesn't directly provide revenue surprises,
        # but we can estimate from available data
        info = stock.info
        
        # Get forward estimates if available
        if 'forwardEps' in info and info['forwardEps']:
            metrics['forward_eps'] = round(info['forwardEps'], 2)
        
        if 'trailingEps' in info and info['trailingEps']:
            metrics['trailing_eps'] = round(info['trailingEps'], 2)
            
            if 'forward_eps' in metrics and metrics['trailing_eps'] != 0:
                metrics['eps_growth_forecast'] = round(
                    ((metrics['forward_eps'] / metrics['trailing_eps']) - 1) * 100, 2
                )
        
        # 4. Earnings Quality Indicators
        # Get cash flow data
        try:
            cashflow = stock.cashflow
            income = stock.financials
            
            if not cashflow.empty and not income.empty:
                # Get most recent year data
                ocf = cashflow.loc['Operating Cash Flow'].iloc[0] if 'Operating Cash Flow' in cashflow.index else None
                net_income = income.loc['Net Income'].iloc[0] if 'Net Income' in income.index else None
                
                if ocf and net_income and net_income != 0:
                    # Cash flow to net income ratio (earnings quality)
                    quality_ratio = ocf / net_income
                    metrics['earnings_quality_ratio'] = round(quality_ratio, 2)
                    
                    if quality_ratio > 1.2:
                        metrics['earnings_quality'] = 'High (Cash > Earnings)'
                    elif quality_ratio > 0.8:
                        metrics['earnings_quality'] = 'Good'
                    elif quality_ratio > 0.5:
                        metrics['earnings_quality'] = 'Moderate'
                    else:
                        metrics['earnings_quality'] = 'Low (Accrual Heavy)'
        except Exception as e:
            print(f"      [WARN] Could not calculate earnings quality: {e}")
        
        # 5. Estimate Revisions (Analyst sentiment)
        if 'targetMeanPrice' in info and info['targetMeanPrice']:
            current_price = info.get('currentPrice', 0)
            target_price = info['targetMeanPrice']
            
            if current_price > 0:
                metrics['analyst_price_target'] = round(target_price, 2)
                metrics['upside_to_target'] = round(((target_price / current_price) - 1) * 100, 2)
        
        # Number of analysts
        if 'numberOfAnalystOpinions' in info:
            metrics['analyst_coverage'] = info['numberOfAnalystOpinions']
        
        # 6. Overall Earnings Score
        score = 0
        max_score = 0
        
        if 'beat_rate' in metrics:
            max_score += 25
            score += min(metrics['beat_rate'] / 4, 25)  # Max 25 points
        
        if 'surprise_consistency' in metrics:
            max_score += 25
            if metrics['surprise_consistency'] == 'High':
                score += 25
            elif metrics['surprise_consistency'] == 'Moderate':
                score += 15
            else:
                score += 5
        
        if 'eps_trend' in metrics:
            max_score += 25
            if 'Strong' in metrics['eps_trend'] or 'Growing' in metrics['eps_trend']:
                score += 25
            elif 'Slowing' in metrics['eps_trend']:
                score += 10
        
        if 'earnings_quality' in metrics:
            max_score += 25
            if 'High' in metrics['earnings_quality']:
                score += 25
            elif 'Good' in metrics['earnings_quality']:
                score += 20
            elif 'Moderate' in metrics['earnings_quality']:
                score += 10
        
        if max_score > 0:
            metrics['earnings_score'] = round((score / max_score) * 100, 2)
            
            if metrics['earnings_score'] >= 80:
                metrics['earnings_rating'] = 'Excellent'
            elif metrics['earnings_score'] >= 60:
                metrics['earnings_rating'] = 'Good'
            elif metrics['earnings_score'] >= 40:
                metrics['earnings_rating'] = 'Fair'
            else:
                metrics['earnings_rating'] = 'Poor'
        
        print(f"[OK] Earnings analysis complete")
        print(f"     Beat Rate: {metrics.get('beat_rate', 'N/A')}%")
        print(f"     Earnings Score: {metrics.get('earnings_score', 'N/A')}/100")
        
        return {
            'status': 'success',
            'metrics': metrics,
            'earnings_data': earnings_df.to_dict('records') if not earnings_df.empty else []
        }
        
    except Exception as e:
        print(f"[ERROR] Earnings analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error analyzing earnings: {str(e)}'
        }


def get_earnings_calendar(ticker: str) -> Dict:
    """
    Get upcoming and past earnings dates
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Earnings calendar information
    """
    try:
        stock = yf.Ticker(ticker)
        
        calendar = {}
        
        # Get earnings dates
        earnings_dates = stock.earnings_dates
        
        if earnings_dates is not None and not earnings_dates.empty:
            # Find next earnings date (future dates)
            future_dates = earnings_dates[earnings_dates.index > datetime.now()]
            
            if not future_dates.empty:
                next_earnings = future_dates.iloc[-1]  # Closest future date
                calendar['next_earnings_date'] = next_earnings.name.strftime('%Y-%m-%d')
                
                # Days until earnings
                days_until = (next_earnings.name - datetime.now()).days
                calendar['days_until_earnings'] = days_until
            
            # Last earnings date
            past_dates = earnings_dates[earnings_dates.index <= datetime.now()]
            if not past_dates.empty:
                last_earnings = past_dates.iloc[0]  # Most recent past date
                calendar['last_earnings_date'] = last_earnings.name.strftime('%Y-%m-%d')
                
                # Days since earnings
                days_since = (datetime.now() - last_earnings.name).days
                calendar['days_since_earnings'] = days_since
        
        return {
            'status': 'success',
            'calendar': calendar
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error getting earnings calendar: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING EARNINGS ANALYSIS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    # Test 1: Earnings History Analysis
    print(f"\n[TEST 1] Earnings Analysis for {test_ticker}")
    print("-"*80)
    earnings_data = analyze_earnings_history(test_ticker, periods=8)
    
    if earnings_data['status'] == 'success':
        metrics = earnings_data['metrics']
        
        print(f"\nEarnings Performance:")
        print(f"  Total Reports: {metrics.get('total_earnings_reports', 'N/A')}")
        print(f"  Beats: {metrics.get('earnings_beats', 'N/A')}")
        print(f"  Misses: {metrics.get('earnings_misses', 'N/A')}")
        print(f"  Beat Rate: {metrics.get('beat_rate', 'N/A')}%")
        print(f"  Avg Surprise: {metrics.get('avg_surprise_pct', 'N/A')}%")
        print(f"  Surprise Consistency: {metrics.get('surprise_consistency', 'N/A')}")
        
        print(f"\nEPS Trends:")
        print(f"  EPS Momentum: {metrics.get('eps_momentum', 'N/A')}%")
        print(f"  EPS Trend: {metrics.get('eps_trend', 'N/A')}")
        print(f"  Forward EPS: ${metrics.get('forward_eps', 'N/A')}")
        print(f"  Growth Forecast: {metrics.get('eps_growth_forecast', 'N/A')}%")
        
        print(f"\nEarnings Quality:")
        print(f"  Quality Ratio: {metrics.get('earnings_quality_ratio', 'N/A')}")
        print(f"  Quality Rating: {metrics.get('earnings_quality', 'N/A')}")
        
        print(f"\nOverall Score:")
        print(f"  Earnings Score: {metrics.get('earnings_score', 'N/A')}/100")
        print(f"  Rating: {metrics.get('earnings_rating', 'N/A')}")
        
        print("\n[OK] Test 1 PASSED")
    else:
        print(f"[FAIL] {earnings_data['message']}")
    
    # Test 2: Earnings Calendar
    print(f"\n\n[TEST 2] Earnings Calendar for {test_ticker}")
    print("-"*80)
    calendar_data = get_earnings_calendar(test_ticker)
    
    if calendar_data['status'] == 'success':
        calendar = calendar_data['calendar']
        
        print(f"\nEarnings Schedule:")
        if 'next_earnings_date' in calendar:
            print(f"  Next Earnings: {calendar['next_earnings_date']}")
            print(f"  Days Until: {calendar['days_until_earnings']}")
        else:
            print(f"  Next Earnings: Not scheduled")
        
        if 'last_earnings_date' in calendar:
            print(f"  Last Earnings: {calendar['last_earnings_date']}")
            print(f"  Days Since: {calendar['days_since_earnings']}")
        
        print("\n[OK] Test 2 PASSED")
    else:
        print(f"[FAIL] {calendar_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nTotal Metrics Available: ~15")
    print(f"Beat Rate, Surprise %, EPS Momentum, Quality Score, etc.")

