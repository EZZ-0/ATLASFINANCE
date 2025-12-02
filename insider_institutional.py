"""
INSIDER TRADING TRACKER
================================================================================
Tracks insider buying/selling activity from SEC Form 4 filings.

Features:
- Recent insider transactions
- Insider sentiment analysis
- Buy vs Sell ratio
- Transaction size analysis
- Key insider identification

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta


def get_insider_transactions(ticker: str, limit: int = 50) -> Dict:
    """
    Fetch recent insider trading activity
    
    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of transactions to retrieve
        
    Returns:
        Dictionary containing:
            - transactions_df: DataFrame with insider trades
            - summary: Aggregated statistics
            - sentiment: Overall insider sentiment
    """
    try:
        print(f"\n[INFO] Fetching insider transactions for {ticker}...")
        
        stock = yf.Ticker(ticker)
        
        # Get insider transactions
        insider_transactions = stock.insider_transactions
        
        if insider_transactions is None or insider_transactions.empty:
            return {
                'status': 'error',
                'message': f'No insider transaction data available for {ticker}',
                'transactions': None,
                'summary': None,
                'sentiment': 'N/A'
            }
        
        # Limit results
        transactions = insider_transactions.head(limit).copy()
        
        # Analyze transactions
        total_transactions = len(transactions)
        
        # Count buys vs sells
        if 'Shares' in transactions.columns and 'Transaction' in transactions.columns:
            buys = transactions[transactions['Transaction'] == 'Buy']
            sells = transactions[transactions['Transaction'] == 'Sale']
            
            num_buys = len(buys)
            num_sells = len(sells)
            
            # Calculate value
            buy_value = buys['Value'].sum() if 'Value' in buys.columns else buys['Shares'].sum() * buys.get('Price', 0).fillna(0).sum()
            sell_value = sells['Value'].sum() if 'Value' in sells.columns else sells['Shares'].sum() * sells.get('Price', 0).fillna(0).sum()
            
            total_value = buy_value + sell_value
            
        else:
            # Fallback if Transaction column not available
            num_buys = 0
            num_sells = 0
            buy_value = 0
            sell_value = 0
            total_value = 0
        
        # Determine sentiment
        if num_buys + num_sells == 0:
            sentiment = 'Neutral'
            sentiment_score = 0
        else:
            buy_ratio = num_buys / (num_buys + num_sells)
            
            if buy_ratio >= 0.7:
                sentiment = 'Very Bullish'
                sentiment_score = 2
            elif buy_ratio >= 0.55:
                sentiment = 'Bullish'
                sentiment_score = 1
            elif buy_ratio >= 0.45:
                sentiment = 'Neutral'
                sentiment_score = 0
            elif buy_ratio >= 0.3:
                sentiment = 'Bearish'
                sentiment_score = -1
            else:
                sentiment = 'Very Bearish'
                sentiment_score = -2
        
        # Identify key insiders (executives)
        key_titles = ['CEO', 'CFO', 'COO', 'President', 'Chairman', 'Director', 'Chief']
        if 'Insider Trading' in transactions.columns:
            key_insider_transactions = transactions[
                transactions['Insider Trading'].str.contains('|'.join(key_titles), case=False, na=False)
            ]
            num_key_insider_trades = len(key_insider_transactions)
        else:
            num_key_insider_trades = 0
        
        # Recent activity (last 30 days)
        if hasattr(transactions.index, 'to_pydatetime'):
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_transactions = transactions[transactions.index >= thirty_days_ago]
            num_recent = len(recent_transactions)
        else:
            num_recent = 0
        
        summary = {
            'total_transactions': total_transactions,
            'num_buys': num_buys,
            'num_sells': num_sells,
            'buy_value': buy_value,
            'sell_value': sell_value,
            'total_value': total_value,
            'buy_ratio': num_buys / (num_buys + num_sells) if (num_buys + num_sells) > 0 else 0,
            'key_insider_trades': num_key_insider_trades,
            'recent_activity_30d': num_recent,
            'sentiment_score': sentiment_score
        }
        
        print(f"[OK] Retrieved {total_transactions} insider transactions")
        print(f"     Sentiment: {sentiment} (Buys: {num_buys}, Sells: {num_sells})")
        
        return {
            'status': 'success',
            'ticker': ticker,
            'transactions': transactions,
            'summary': summary,
            'sentiment': sentiment,
            'message': 'Successfully retrieved insider trading data'
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch insider transactions: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching insider transactions: {str(e)}',
            'transactions': None,
            'summary': None,
            'sentiment': 'N/A'
        }


def get_institutional_holders(ticker: str) -> Dict:
    """
    Fetch institutional ownership data
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing:
            - holders_df: DataFrame with institutional holders
            - summary: Aggregated statistics
    """
    try:
        print(f"\n[INFO] Fetching institutional holders for {ticker}...")
        
        stock = yf.Ticker(ticker)
        
        # Get institutional holders
        institutional_holders = stock.institutional_holders
        
        if institutional_holders is None or institutional_holders.empty:
            return {
                'status': 'error',
                'message': f'No institutional holder data available for {ticker}',
                'holders': None,
                'summary': None
            }
        
        # Analyze holdings
        total_holders = len(institutional_holders)
        
        if 'Shares' in institutional_holders.columns:
            total_shares_held = institutional_holders['Shares'].sum()
            
            # Get shares outstanding
            try:
                shares_outstanding = stock.info.get('sharesOutstanding', 0)
                institutional_ownership_pct = (total_shares_held / shares_outstanding * 100) if shares_outstanding > 0 else 0
            except:
                institutional_ownership_pct = 0
                shares_outstanding = 0
            
            # Top holder concentration
            if total_shares_held > 0:
                top_5_pct = institutional_holders['Shares'].head(5).sum() / total_shares_held * 100
            else:
                top_5_pct = 0
        else:
            total_shares_held = 0
            institutional_ownership_pct = 0
            top_5_pct = 0
            shares_outstanding = 0
        
        summary = {
            'total_holders': total_holders,
            'total_shares_held': total_shares_held,
            'institutional_ownership_pct': institutional_ownership_pct,
            'top_5_concentration': top_5_pct,
            'shares_outstanding': shares_outstanding
        }
        
        print(f"[OK] Retrieved {total_holders} institutional holders")
        print(f"     Institutional Ownership: {institutional_ownership_pct:.1f}%")
        
        return {
            'status': 'success',
            'ticker': ticker,
            'holders': institutional_holders,
            'summary': summary,
            'message': 'Successfully retrieved institutional holder data'
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch institutional holders: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching institutional holders: {str(e)}',
            'holders': None,
            'summary': None
        }


def get_major_holders(ticker: str) -> Dict:
    """
    Get major holders summary (quick stats)
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary with major holder statistics
    """
    try:
        stock = yf.Ticker(ticker)
        major_holders = stock.major_holders
        
        if major_holders is None or major_holders.empty:
            return {
                'status': 'error',
                'message': 'No major holder data available'
            }
        
        # Parse major holders data
        data_dict = {}
        for idx, row in major_holders.iterrows():
            key = row[1] if len(row) > 1 else f"metric_{idx}"
            value = row[0]
            data_dict[key] = value
        
        return {
            'status': 'success',
            'data': data_dict
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING INSIDER TRADING & INSTITUTIONAL HOLDERS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    # Test 1: Insider Transactions
    print(f"\n[TEST 1] Insider Transactions for {test_ticker}")
    print("-"*80)
    insider_data = get_insider_transactions(test_ticker, limit=20)
    
    if insider_data['status'] == 'success':
        summary = insider_data['summary']
        print(f"\nSentiment: {insider_data['sentiment']}")
        print(f"Total Transactions: {summary['total_transactions']}")
        print(f"Buys: {summary['num_buys']}")
        print(f"Sells: {summary['num_sells']}")
        print(f"Buy Ratio: {summary['buy_ratio']*100:.1f}%")
        print(f"Recent Activity (30d): {summary['recent_activity_30d']}")
        
        if not insider_data['transactions'].empty:
            print(f"\nRecent Transactions (first 5):")
            print(insider_data['transactions'].head().to_string())
        
        print("\n[OK] Test 1 PASSED")
    else:
        print(f"[WARN] {insider_data['message']}")
    
    # Test 2: Institutional Holders
    print(f"\n\n[TEST 2] Institutional Holders for {test_ticker}")
    print("-"*80)
    institutional_data = get_institutional_holders(test_ticker)
    
    if institutional_data['status'] == 'success':
        summary = institutional_data['summary']
        print(f"\nTotal Institutional Holders: {summary['total_holders']}")
        print(f"Institutional Ownership: {summary['institutional_ownership_pct']:.2f}%")
        print(f"Top 5 Concentration: {summary['top_5_concentration']:.2f}%")
        print(f"Total Shares Held: {summary['total_shares_held']:,.0f}")
        
        if not institutional_data['holders'].empty:
            print(f"\nTop 10 Institutional Holders:")
            print(institutional_data['holders'].head(10).to_string())
        
        print("\n[OK] Test 2 PASSED")
    else:
        print(f"[WARN] {institutional_data['message']}")
    
    # Test 3: Major Holders
    print(f"\n\n[TEST 3] Major Holders Summary for {test_ticker}")
    print("-"*80)
    major_data = get_major_holders(test_ticker)
    
    if major_data['status'] == 'success':
        print("\nMajor Holder Statistics:")
        for key, value in major_data['data'].items():
            print(f"  {key}: {value}")
        print("\n[OK] Test 3 PASSED")
    else:
        print(f"[WARN] {major_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)





