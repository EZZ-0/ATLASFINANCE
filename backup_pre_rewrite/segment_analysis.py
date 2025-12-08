"""
SEGMENT ANALYSIS MODULE
================================================================================
Analyze company revenue by geographic region and business segment.

Features:
- Geographic revenue breakdown
- Business segment performance
- Segment growth analysis
- Segment profitability (if available)

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List


def get_segment_data(ticker: str) -> Dict:
    """
    Fetch and analyze company segment data
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Dictionary containing segment analysis
    """
    try:
        print(f"\n[INFO] Fetching segment data for {ticker}...")
        
        stock = yf.Ticker(ticker)
        
        # Try to get segment data from financials
        # Note: yfinance doesn't have dedicated segment API, so we'll use info
        info = stock.info
        
        # Get company description and business summary
        business_summary = info.get('longBusinessSummary', '')
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        
        # Get revenue by geography (if available in info)
        # This is limited in yfinance, but we'll extract what we can
        
        # Get key statistics
        total_revenue = info.get('totalRevenue', 0)
        market_cap = info.get('marketCap', 0)
        employees = info.get('fullTimeEmployees', 0)
        
        # Try to get revenue growth by region (limited data)
        revenue_per_employee = total_revenue / employees if employees > 0 else 0
        
        # Parse business summary for segment clues
        segments_found = []
        segment_keywords = {
            'Geographic': ['Americas', 'Europe', 'Asia', 'China', 'North America', 
                          'EMEA', 'APAC', 'Latin America', 'Middle East'],
            'Business': ['Products', 'Services', 'Software', 'Hardware', 
                        'Cloud', 'Subscription', 'Advertising', 'Retail']
        }
        
        for category, keywords in segment_keywords.items():
            found = [kw for kw in keywords if kw.lower() in business_summary.lower()]
            if found:
                segments_found.append({
                    'category': category,
                    'segments': found
                })
        
        # Get latest financials for segment clues
        income_stmt = stock.financials
        
        # Check if we have any segment-level data
        has_segment_data = False
        segment_breakdown = {}
        
        # yfinance limitation: Detailed segment data not available
        # We'll provide what's available
        
        print(f"[OK] Company profile retrieved")
        print(f"     Sector: {sector}")
        print(f"     Industry: {industry}")
        print(f"     Segments identified: {len(segments_found)}")
        
        return {
            'status': 'success',
            'ticker': ticker,
            'company_profile': {
                'sector': sector,
                'industry': industry,
                'employees': employees,
                'total_revenue': total_revenue,
                'market_cap': market_cap,
                'revenue_per_employee': revenue_per_employee
            },
            'business_summary': business_summary,
            'segments_identified': segments_found,
            'has_detailed_segments': has_segment_data,
            'segment_breakdown': segment_breakdown,
            'message': 'Company profile retrieved. Note: Detailed segment data requires SEC filings.',
            'recommendation': 'For detailed segment analysis, refer to 10-K Section "Segment Information"'
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch segment data: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching segment data: {str(e)}',
            'company_profile': None,
            'segments_identified': []
        }


def analyze_business_mix(ticker: str) -> Dict:
    """
    Analyze business model and revenue mix
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Business model analysis
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get key business metrics
        business_model = {
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'business_type': info.get('quoteType', 'N/A'),
            'revenue_model': []
        }
        
        # Infer revenue model from description
        summary = info.get('longBusinessSummary', '').lower()
        
        revenue_indicators = {
            'Product Sales': ['sells', 'products', 'manufacturing', 'retail'],
            'Services': ['services', 'consulting', 'support'],
            'Subscription': ['subscription', 'recurring', 'saas', 'cloud'],
            'Advertising': ['advertising', 'ads', 'ad-supported'],
            'Transaction Fees': ['transaction', 'payment', 'processing'],
            'Licensing': ['licensing', 'royalty', 'intellectual property']
        }
        
        for model, keywords in revenue_indicators.items():
            if any(kw in summary for kw in keywords):
                business_model['revenue_model'].append(model)
        
        return {
            'status': 'success',
            'business_model': business_model,
            'summary': summary[:500]  # First 500 chars
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error analyzing business mix: {str(e)}'
        }


def get_competitive_position(ticker: str) -> Dict:
    """
    Analyze competitive position and market share indicators
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Competitive analysis
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get competitive metrics
        competitive_data = {
            'market_cap': info.get('marketCap', 0),
            'enterprise_value': info.get('enterpriseValue', 0),
            'revenue': info.get('totalRevenue', 0),
            'employees': info.get('fullTimeEmployees', 0),
            'profit_margin': info.get('profitMargins', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
        }
        
        # Calculate efficiency metrics
        if competitive_data['employees'] > 0:
            competitive_data['revenue_per_employee'] = competitive_data['revenue'] / competitive_data['employees']
            competitive_data['market_cap_per_employee'] = competitive_data['market_cap'] / competitive_data['employees']
        else:
            competitive_data['revenue_per_employee'] = 0
            competitive_data['market_cap_per_employee'] = 0
        
        # Competitive positioning
        if competitive_data['market_cap'] > 200e9:
            position = 'Mega Cap (Market Leader)'
        elif competitive_data['market_cap'] > 10e9:
            position = 'Large Cap (Established Player)'
        elif competitive_data['market_cap'] > 2e9:
            position = 'Mid Cap (Growing Company)'
        else:
            position = 'Small Cap (Emerging Player)'
        
        return {
            'status': 'success',
            'competitive_metrics': competitive_data,
            'market_position': position
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error analyzing competitive position: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING SEGMENT ANALYSIS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    # Test 1: Segment Data
    print(f"\n[TEST 1] Segment Analysis for {test_ticker}")
    print("-"*80)
    segment_data = get_segment_data(test_ticker)
    
    if segment_data['status'] == 'success':
        profile = segment_data['company_profile']
        print(f"\nCompany Profile:")
        print(f"  Sector: {profile['sector']}")
        print(f"  Industry: {profile['industry']}")
        print(f"  Employees: {profile['employees']:,}")
        print(f"  Total Revenue: ${profile['total_revenue']/1e9:.2f}B")
        print(f"  Market Cap: ${profile['market_cap']/1e9:.2f}B")
        print(f"  Revenue per Employee: ${profile['revenue_per_employee']:,.0f}")
        
        if segment_data['segments_identified']:
            print(f"\nSegments Identified from Business Summary:")
            for seg in segment_data['segments_identified']:
                print(f"  {seg['category']}: {', '.join(seg['segments'])}")
        
        print(f"\n{segment_data['recommendation']}")
        print("\n[OK] Test 1 PASSED")
    else:
        print(f"[FAIL] {segment_data['message']}")
    
    # Test 2: Business Mix
    print(f"\n\n[TEST 2] Business Mix Analysis for {test_ticker}")
    print("-"*80)
    business_data = analyze_business_mix(test_ticker)
    
    if business_data['status'] == 'success':
        model = business_data['business_model']
        print(f"\nBusiness Model:")
        print(f"  Sector: {model['sector']}")
        print(f"  Industry: {model['industry']}")
        print(f"  Type: {model['business_type']}")
        if model['revenue_model']:
            print(f"  Revenue Streams: {', '.join(model['revenue_model'])}")
        
        print(f"\nBusiness Summary (excerpt):")
        print(f"  {business_data['summary'][:200]}...")
        
        print("\n[OK] Test 2 PASSED")
    else:
        print(f"[FAIL] {business_data['message']}")
    
    # Test 3: Competitive Position
    print(f"\n\n[TEST 3] Competitive Position for {test_ticker}")
    print("-"*80)
    competitive_data = get_competitive_position(test_ticker)
    
    if competitive_data['status'] == 'success':
        metrics = competitive_data['competitive_metrics']
        print(f"\nCompetitive Metrics:")
        print(f"  Market Position: {competitive_data['market_position']}")
        print(f"  Market Cap: ${metrics['market_cap']/1e9:.2f}B")
        print(f"  Enterprise Value: ${metrics['enterprise_value']/1e9:.2f}B")
        print(f"  Revenue: ${metrics['revenue']/1e9:.2f}B")
        print(f"  Employees: {metrics['employees']:,}")
        print(f"  Revenue/Employee: ${metrics['revenue_per_employee']:,.0f}")
        print(f"  Market Cap/Employee: ${metrics['market_cap_per_employee']:,.0f}")
        print(f"  Profit Margin: {metrics['profit_margin']*100:.2f}%")
        print(f"  Revenue Growth: {metrics['revenue_growth']*100:.2f}%")
        
        print("\n[OK] Test 3 PASSED")
    else:
        print(f"[FAIL] {competitive_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print("\nNOTE: Detailed segment data (geographic/business breakdowns)")
    print("requires SEC 10-K filings. This module provides company profile")
    print("and competitive analysis based on available yfinance data.")





