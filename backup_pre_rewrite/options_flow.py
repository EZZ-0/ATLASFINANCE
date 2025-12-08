"""
OPTIONS FLOW ANALYSIS MODULE
================================================================================
Analyze options market activity and sentiment.

Features:
- Put/Call Ratio
- Implied Volatility
- Open Interest Analysis
- Options Volume
- Greeks Summary

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime, timedelta


def get_options_data(ticker: str) -> Dict:
    """
    Fetch options data and analyze options flow
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing options analysis
    """
    try:
        print(f"\n[INFO] Fetching options data for {ticker}...")
        
        stock = yf.Ticker(ticker)
        
        # Get available expiration dates
        expiration_dates = stock.options
        
        if not expiration_dates or len(expiration_dates) == 0:
            return {
                'status': 'error',
                'message': f'No options data available for {ticker}',
                'put_call_ratio': None,
                'implied_volatility': None
            }
        
        # Get options chain for nearest expiration
        nearest_exp = expiration_dates[0]
        opt_chain = stock.option_chain(nearest_exp)
        
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        if calls.empty or puts.empty:
            return {
                'status': 'error',
                'message': f'Empty options chain for {ticker}',
                'put_call_ratio': None,
                'implied_volatility': None
            }
        
        # Calculate Put/Call Ratio (Volume-based)
        total_call_volume = calls['volume'].fillna(0).sum()
        total_put_volume = puts['volume'].fillna(0).sum()
        
        if total_call_volume > 0:
            pc_ratio_volume = total_put_volume / total_call_volume
        else:
            pc_ratio_volume = None
        
        # Calculate Put/Call Ratio (Open Interest-based)
        total_call_oi = calls['openInterest'].fillna(0).sum()
        total_put_oi = puts['openInterest'].fillna(0).sum()
        
        if total_call_oi > 0:
            pc_ratio_oi = total_put_oi / total_call_oi
        else:
            pc_ratio_oi = None
        
        # Calculate average implied volatility
        call_iv_avg = calls['impliedVolatility'].fillna(0).mean()
        put_iv_avg = puts['impliedVolatility'].fillna(0).mean()
        overall_iv = (call_iv_avg + put_iv_avg) / 2
        
        # Find most active options (by volume)
        calls_sorted = calls.sort_values('volume', ascending=False).head(5)
        puts_sorted = puts.sort_values('volume', ascending=False).head(5)
        
        # Analyze sentiment based on Put/Call Ratio
        if pc_ratio_volume:
            if pc_ratio_volume < 0.7:
                sentiment = 'Bullish'
                sentiment_desc = 'More call buying than put buying'
            elif pc_ratio_volume < 1.0:
                sentiment = 'Slightly Bullish'
                sentiment_desc = 'Moderate call preference'
            elif pc_ratio_volume <= 1.3:
                sentiment = 'Neutral'
                sentiment_desc = 'Balanced options activity'
            elif pc_ratio_volume <= 1.7:
                sentiment = 'Slightly Bearish'
                sentiment_desc = 'Moderate put preference'
            else:
                sentiment = 'Bearish'
                sentiment_desc = 'More put buying than call buying'
        else:
            sentiment = 'Unknown'
            sentiment_desc = 'Insufficient data'
        
        # Get current stock price
        try:
            current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
        except:
            current_price = None
        
        # Analyze moneyness
        if current_price:
            calls['moneyness'] = (calls['strike'] - current_price) / current_price * 100
            puts['moneyness'] = (current_price - puts['strike']) / current_price * 100
            
            # Find ATM options (within 5% of current price)
            atm_calls = calls[np.abs(calls['moneyness']) < 5]
            atm_puts = puts[np.abs(puts['moneyness']) < 5]
            
            atm_call_volume = atm_calls['volume'].fillna(0).sum()
            atm_put_volume = atm_puts['volume'].fillna(0).sum()
        else:
            atm_call_volume = 0
            atm_put_volume = 0
        
        print(f"[OK] Options data retrieved")
        print(f"     Put/Call Ratio: {pc_ratio_volume:.2f}" if pc_ratio_volume else "     Put/Call Ratio: N/A")
        print(f"     Sentiment: {sentiment}")
        print(f"     Implied Volatility: {overall_iv*100:.2f}%")
        
        return {
            'status': 'success',
            'ticker': ticker,
            'expiration_date': nearest_exp,
            'put_call_ratio': {
                'volume_based': pc_ratio_volume,
                'oi_based': pc_ratio_oi
            },
            'implied_volatility': {
                'calls': call_iv_avg,
                'puts': put_iv_avg,
                'overall': overall_iv
            },
            'volume': {
                'total_calls': total_call_volume,
                'total_puts': total_put_volume,
                'atm_calls': atm_call_volume,
                'atm_puts': atm_put_volume
            },
            'open_interest': {
                'total_calls': total_call_oi,
                'total_puts': total_put_oi
            },
            'most_active': {
                'calls': calls_sorted[['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']],
                'puts': puts_sorted[['strike', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']]
            },
            'sentiment': sentiment,
            'sentiment_description': sentiment_desc,
            'current_price': current_price,
            'calls_df': calls,
            'puts_df': puts,
            'message': 'Successfully retrieved options data'
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch options data: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching options data: {str(e)}',
            'put_call_ratio': None,
            'implied_volatility': None
        }


def analyze_options_greeks(ticker: str) -> Dict:
    """
    Analyze options Greeks (if available)
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with Greeks analysis
    """
    try:
        stock = yf.Ticker(ticker)
        expiration_dates = stock.options
        
        if not expiration_dates or len(expiration_dates) == 0:
            return {'status': 'error', 'message': 'No options available'}
        
        opt_chain = stock.option_chain(expiration_dates[0])
        calls = opt_chain.calls
        puts = opt_chain.puts
        
        # Check if Greeks are available
        greeks_available = ['delta', 'gamma', 'theta', 'vega']
        available_greeks = [g for g in greeks_available if g in calls.columns]
        
        if not available_greeks:
            return {
                'status': 'partial',
                'message': 'Greeks not available in data',
                'available_greeks': []
            }
        
        # Calculate average Greeks
        greeks_summary = {}
        for greek in available_greeks:
            greeks_summary[f'call_{greek}'] = calls[greek].mean()
            greeks_summary[f'put_{greek}'] = puts[greek].mean()
        
        return {
            'status': 'success',
            'available_greeks': available_greeks,
            'summary': greeks_summary
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error analyzing Greeks: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING OPTIONS FLOW ANALYSIS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    # Test 1: Options Data
    print(f"\n[TEST 1] Options Flow Analysis for {test_ticker}")
    print("-"*80)
    options_data = get_options_data(test_ticker)
    
    if options_data['status'] == 'success':
        print(f"\nExpiration Date: {options_data['expiration_date']}")
        print(f"Current Price: ${options_data['current_price']:.2f}")
        
        print(f"\n--- PUT/CALL RATIO ---")
        pcr = options_data['put_call_ratio']
        print(f"Volume-Based: {pcr['volume_based']:.2f}")
        print(f"OI-Based: {pcr['oi_based']:.2f}")
        
        print(f"\n--- IMPLIED VOLATILITY ---")
        iv = options_data['implied_volatility']
        print(f"Overall IV: {iv['overall']*100:.2f}%")
        print(f"Call IV: {iv['calls']*100:.2f}%")
        print(f"Put IV: {iv['puts']*100:.2f}%")
        
        print(f"\n--- VOLUME ANALYSIS ---")
        vol = options_data['volume']
        print(f"Total Call Volume: {vol['total_calls']:,.0f}")
        print(f"Total Put Volume: {vol['total_puts']:,.0f}")
        print(f"ATM Call Volume: {vol['atm_calls']:,.0f}")
        print(f"ATM Put Volume: {vol['atm_puts']:,.0f}")
        
        print(f"\n--- OPEN INTEREST ---")
        oi = options_data['open_interest']
        print(f"Total Call OI: {oi['total_calls']:,.0f}")
        print(f"Total Put OI: {oi['total_puts']:,.0f}")
        
        print(f"\n--- SENTIMENT ---")
        print(f"Overall: {options_data['sentiment']}")
        print(f"Description: {options_data['sentiment_description']}")
        
        print(f"\n--- MOST ACTIVE CALLS (Top 5) ---")
        print(options_data['most_active']['calls'].to_string())
        
        print(f"\n--- MOST ACTIVE PUTS (Top 5) ---")
        print(options_data['most_active']['puts'].to_string())
        
        print("\n[OK] Test 1 PASSED")
    else:
        print(f"[FAIL] {options_data['message']}")
    
    # Test 2: Greeks Analysis
    print(f"\n\n[TEST 2] Options Greeks for {test_ticker}")
    print("-"*80)
    greeks_data = analyze_options_greeks(test_ticker)
    
    if greeks_data['status'] == 'success':
        print(f"\nAvailable Greeks: {', '.join(greeks_data['available_greeks'])}")
        print(f"\nGreeks Summary:")
        for key, value in greeks_data['summary'].items():
            print(f"  {key}: {value:.4f}")
        print("\n[OK] Test 2 PASSED")
    elif greeks_data['status'] == 'partial':
        print(f"[WARN] {greeks_data['message']}")
        print("[OK] Test 2 PASSED (partial data)")
    else:
        print(f"[WARN] {greeks_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)





