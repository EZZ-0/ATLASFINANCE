"""
ANALYST RATINGS & PRICE TARGETS MODULE
================================================================================
Extracts and analyzes Wall Street analyst recommendations and price targets.

Features:
- Consensus rating (Strong Buy, Buy, Hold, Sell, Strong Sell)
- Buy/Hold/Sell recommendation counts
- Current price vs. Target price comparison
- Upside/Downside potential
- Rating distribution analysis

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Any

# Import centralized cache to prevent Yahoo rate limiting
from utils.ticker_cache import get_ticker_info, get_ticker


def get_analyst_ratings(ticker: str, financials: Dict = None) -> Dict[str, Any]:
    """
    Fetches analyst ratings and price targets for a given ticker.
    
    Args:
        ticker (str): Stock ticker symbol (e.g., 'AAPL')
        
    Returns:
        dict: Dictionary containing:
            - status: 'success' or 'error'
            - recommendations: DataFrame with rating counts over time
            - price_target: Dict with current, target, upside %
            - consensus_rating: String representation of consensus
            - rating_distribution: Dict with current period counts
            - message: Error message if applicable
    """
    try:
        print(f"\n[INFO] Fetching analyst ratings for {ticker}...")
        
        # Use pre-extracted info if available, otherwise use centralized cache
        if financials and 'info' in financials:
            info = financials['info']
            print(f"   [REUSE] Using pre-extracted info data")
        else:
            info = get_ticker_info(ticker)
        
        # Need Ticker object for recommendations (not cached)
        stock = get_ticker(ticker)
        
        # Get recommendations
        recommendations = stock.recommendations
        if recommendations is None or recommendations.empty:
            return {
                'status': 'error',
                'message': f'No analyst recommendations available for {ticker}',
                'recommendations': None,
                'price_target': None,
                'consensus_rating': 'N/A',
                'rating_distribution': None
            }
        
        # Get current stock price from cached info
        try:
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            if current_price is None:
                # Fallback: get from history
                hist = stock.history(period='1d')
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
        except (KeyError, IndexError, TypeError, AttributeError):
            current_price = None
        
        # Get price targets from cached info
        try:
            target_high = info.get('targetHighPrice')
            target_low = info.get('targetLowPrice')
            target_mean = info.get('targetMeanPrice')
            target_median = info.get('targetMedianPrice')
            num_analysts = info.get('numberOfAnalystOpinions')
        except (KeyError, TypeError, AttributeError):
            target_high = None
            target_low = None
            target_mean = None
            target_median = None
            num_analysts = None
        
        # Calculate upside/downside
        if current_price and target_mean:
            upside_pct = ((target_mean - current_price) / current_price) * 100
        else:
            upside_pct = None
        
        # Analyze most recent recommendations
        # Group by period (usually monthly) and get latest
        latest_recs = recommendations.tail(30)  # Last 30 entries (roughly 6 months)
        
        # Count recommendation types in recent period
        rating_counts = {
            'strongBuy': 0,
            'buy': 0,
            'hold': 0,
            'sell': 0,
            'strongSell': 0
        }
        
        # Sum up the counts from recent recommendations
        for col in ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']:
            if col in latest_recs.columns:
                rating_counts[col] = int(latest_recs[col].sum())
        
        # Calculate consensus rating
        total_ratings = sum(rating_counts.values())
        if total_ratings > 0:
            # Weighted score: StrongBuy=1, Buy=2, Hold=3, Sell=4, StrongSell=5
            weighted_score = (
                rating_counts['strongBuy'] * 1 +
                rating_counts['buy'] * 2 +
                rating_counts['hold'] * 3 +
                rating_counts['sell'] * 4 +
                rating_counts['strongSell'] * 5
            ) / total_ratings
            
            # Map weighted score to consensus rating
            if weighted_score <= 1.5:
                consensus = 'Strong Buy'
            elif weighted_score <= 2.5:
                consensus = 'Buy'
            elif weighted_score <= 3.5:
                consensus = 'Hold'
            elif weighted_score <= 4.5:
                consensus = 'Sell'
            else:
                consensus = 'Strong Sell'
        else:
            consensus = 'N/A'
            weighted_score = None
        
        print(f"[OK] Analyst ratings fetched successfully")
        print(f"     Consensus: {consensus}")
        if target_mean:
            print(f"     Price Target: ${target_mean:.2f} ({upside_pct:+.1f}% from current)")
        
        return {
            'status': 'success',
            'ticker': ticker,
            'current_price': current_price,
            'price_target': {
                'mean': target_mean,
                'median': target_median,
                'high': target_high,
                'low': target_low,
                'upside_pct': upside_pct
            },
            'consensus_rating': consensus,
            'consensus_score': weighted_score,
            'rating_distribution': rating_counts,
            'total_analysts': total_ratings or num_analysts,
            'recommendations_df': recommendations,
            'message': 'Successfully retrieved analyst ratings'
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch analyst ratings: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching analyst ratings: {str(e)}',
            'recommendations': None,
            'price_target': None,
            'consensus_rating': 'N/A',
            'rating_distribution': None
        }


def format_rating_summary(ratings_data: Dict[str, Any]) -> str:
    """
    Formats analyst ratings data into a human-readable summary.
    
    Args:
        ratings_data (dict): Output from get_analyst_ratings()
        
    Returns:
        str: Formatted summary text
    """
    if ratings_data['status'] != 'success':
        return f"Error: {ratings_data['message']}"
    
    summary = []
    summary.append(f"Analyst Ratings for {ratings_data['ticker']}:")
    summary.append("-" * 50)
    
    # Consensus
    summary.append(f"Consensus Rating: {ratings_data['consensus_rating']}")
    if ratings_data['total_analysts']:
        summary.append(f"Number of Analysts: {ratings_data['total_analysts']}")
    
    # Price targets
    if ratings_data['price_target']['mean']:
        pt = ratings_data['price_target']
        summary.append(f"\nPrice Targets:")
        summary.append(f"  Current Price: ${ratings_data['current_price']:.2f}")
        summary.append(f"  Mean Target:   ${pt['mean']:.2f} ({pt['upside_pct']:+.1f}%)")
        if pt['median']:
            summary.append(f"  Median Target: ${pt['median']:.2f}")
        if pt['high'] and pt['low']:
            summary.append(f"  Range:         ${pt['low']:.2f} - ${pt['high']:.2f}")
    
    # Distribution
    if ratings_data['rating_distribution']:
        dist = ratings_data['rating_distribution']
        summary.append(f"\nRating Distribution:")
        summary.append(f"  Strong Buy: {dist['strongBuy']}")
        summary.append(f"  Buy:        {dist['buy']}")
        summary.append(f"  Hold:       {dist['hold']}")
        summary.append(f"  Sell:       {dist['sell']}")
        summary.append(f"  Strong Sell:{dist['strongSell']}")
    
    return "\n".join(summary)


def get_recommendation_trend(ticker: str, periods: int = 6) -> Optional[pd.DataFrame]:
    """
    Gets the trend of analyst recommendations over recent periods.
    
    Args:
        ticker (str): Stock ticker symbol
        periods (int): Number of recent periods to analyze (default: 6)
        
    Returns:
        pd.DataFrame: Trend data with columns for each rating type
    """
    try:
        # Use centralized cache to get Ticker object
        stock = get_ticker(ticker)
        recommendations = stock.recommendations
        
        if recommendations is None or recommendations.empty:
            return None
        
        # Get most recent periods
        trend_data = recommendations.tail(periods).copy()
        
        # Reset index to make dates a column
        trend_data = trend_data.reset_index()
        
        return trend_data
        
    except Exception as e:
        print(f"[ERROR] Failed to get recommendation trend: {str(e)}")
        return None


# ============================================================================
# TESTING CODE (Run this file directly to test)
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING ANALYST RATINGS MODULE")
    print("="*80)
    
    # Test with AAPL
    test_ticker = "AAPL"
    
    print(f"\n[TEST 1] Getting ratings for {test_ticker}...")
    ratings = get_analyst_ratings(test_ticker)
    
    if ratings['status'] == 'success':
        print("\n" + format_rating_summary(ratings))
        print("\n[OK] Test 1 passed!")
    else:
        print(f"\n[FAIL] Test 1 failed: {ratings['message']}")
    
    print("\n" + "="*80)
    print(f"[TEST 2] Getting recommendation trend for {test_ticker}...")
    trend = get_recommendation_trend(test_ticker)
    
    if trend is not None:
        print("\nRecent Recommendation Trend:")
        print(trend.to_string())
        print("\n[OK] Test 2 passed!")
    else:
        print("\n[FAIL] Test 2 failed")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)





