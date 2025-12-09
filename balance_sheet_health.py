"""
BALANCE SHEET HEALTH MODULE
================================================================================
Comprehensive balance sheet strength, liquidity, and leverage analysis.

Features:
- Liquidity ratios (Current, Quick, Cash)
- Leverage ratios (Debt/Equity, Debt/Assets, Interest Coverage)
- Working capital analysis
- Asset quality metrics
- Net working capital trends
- Balance sheet efficiency
- Financial flexibility score

Data Source: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, Optional


@st.cache_data(ttl=3600)  # Cache for 1 hour
def analyze_balance_sheet_health(ticker: str, _financials: Dict = None) -> Dict:
    """
    Comprehensive balance sheet health analysis
    
    Args:
        ticker: Stock ticker symbol
        financials: Pre-extracted financials dict (optional, reduces API calls)
        
    Returns:
        Dictionary with balance sheet metrics and health score
    """
    try:
        print(f"\n[INFO] Analyzing balance sheet health for {ticker}...")
        
        # Use pre-extracted data if available
        if _financials:
            info = _financials.get('info', {})
            balance_sheet = _financials.get('balance_sheet', pd.DataFrame())
            income_stmt = _financials.get('income_statement', pd.DataFrame())
            print(f"   [REUSE] Using pre-extracted data")
        else:
            # Fallback to direct yfinance call
            stock = yf.Ticker(ticker)
            info = stock.info
            balance_sheet = stock.balance_sheet
            income_stmt = stock.financials
        
        if balance_sheet.empty:
            return {
                'status': 'error',
                'message': 'No balance sheet data available'
            }
        
        metrics = {}
        
        # ====================================
        # 1. LIQUIDITY RATIOS
        # ====================================
        
        # Get latest balance sheet data
        bs = balance_sheet.iloc[:, 0]  # Most recent year
        
        # Current Assets & Liabilities
        current_assets = None
        current_liabilities = None
        cash = None
        inventory = None
        ca_key = None
        cl_key = None
        
        # Try yfinance format first, then SEC format
        for key in ['Current Assets', 'Total Current Assets', 'CurrentAssets', 'Current_Assets']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    current_assets = float(val)
                    ca_key = key
                    break
        
        for key in ['Current Liabilities', 'Total Current Liabilities', 'CurrentLiabilities', 'Current_Liabilities']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    current_liabilities = float(val)
                    cl_key = key
                    break
        
        for key in ['Cash', 'Cash And Cash Equivalents', 'Cash Cash Equivalents And Short Term Investments', 'CashAndCashEquivalentsAtCarryingValue', 'Cash_And_Cash_Equivalents']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    cash = float(val)
                    break
        
        for key in ['Inventory', 'Inventories']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    inventory = float(val)
                    break
        
        # Current Ratio
        if current_assets and current_liabilities and current_liabilities > 0:
            current_ratio = current_assets / current_liabilities
            metrics['current_ratio'] = round(current_ratio, 2)
            
            if current_ratio >= 2:
                metrics['current_ratio_health'] = 'Excellent'
            elif current_ratio >= 1.5:
                metrics['current_ratio_health'] = 'Good'
            elif current_ratio >= 1:
                metrics['current_ratio_health'] = 'Adequate'
            else:
                metrics['current_ratio_health'] = 'Weak'
        
        # Quick Ratio (Acid Test)
        if current_assets and current_liabilities and inventory is not None and current_liabilities > 0:
            quick_ratio = (current_assets - inventory) / current_liabilities
            metrics['quick_ratio'] = round(quick_ratio, 2)
            
            if quick_ratio >= 1.5:
                metrics['quick_ratio_health'] = 'Excellent'
            elif quick_ratio >= 1:
                metrics['quick_ratio_health'] = 'Good'
            elif quick_ratio >= 0.5:
                metrics['quick_ratio_health'] = 'Adequate'
            else:
                metrics['quick_ratio_health'] = 'Weak'
        
        # Cash Ratio
        if cash and current_liabilities and current_liabilities > 0:
            cash_ratio = cash / current_liabilities
            metrics['cash_ratio'] = round(cash_ratio, 2)
            
            if cash_ratio >= 0.5:
                metrics['cash_ratio_health'] = 'Excellent'
            elif cash_ratio >= 0.3:
                metrics['cash_ratio_health'] = 'Good'
            elif cash_ratio >= 0.1:
                metrics['cash_ratio_health'] = 'Adequate'
            else:
                metrics['cash_ratio_health'] = 'Weak'
        
        # ====================================
        # 2. LEVERAGE RATIOS
        # ====================================
        
        # Total Debt & Equity
        total_debt = None
        total_equity = None
        total_assets = None
        
        for key in ['Total Debt', 'Long Term Debt', 'Net Debt', 'Total_Debt', 'LongTermDebt']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    total_debt = float(val)
                    break
        
        for key in ['Stockholders Equity', 'Total Equity', 'Total Stockholder Equity', 'Total_Equity', 'StockholdersEquity']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    total_equity = float(val)
                    break
        
        for key in ['Total Assets', 'Total_Assets', 'Assets']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    total_assets = float(val)
                    break
        
        # Debt-to-Equity Ratio
        if total_debt and total_equity and total_equity > 0:
            debt_to_equity = total_debt / total_equity
            metrics['debt_to_equity'] = round(debt_to_equity, 2)
            
            if debt_to_equity < 0.3:
                metrics['debt_to_equity_health'] = 'Conservative (Low Leverage)'
            elif debt_to_equity < 0.5:
                metrics['debt_to_equity_health'] = 'Healthy'
            elif debt_to_equity < 1:
                metrics['debt_to_equity_health'] = 'Moderate'
            elif debt_to_equity < 2:
                metrics['debt_to_equity_health'] = 'High Leverage'
            else:
                metrics['debt_to_equity_health'] = 'Risky (Very High Leverage)'
        
        # Debt-to-Assets Ratio
        if total_debt and total_assets and total_assets > 0:
            debt_to_assets = total_debt / total_assets
            metrics['debt_to_assets'] = round(debt_to_assets, 2)
            
            if debt_to_assets < 0.3:
                metrics['debt_to_assets_health'] = 'Low Risk'
            elif debt_to_assets < 0.5:
                metrics['debt_to_assets_health'] = 'Moderate Risk'
            else:
                metrics['debt_to_assets_health'] = 'High Risk'
        
        # Equity Ratio
        if total_equity and total_assets and total_assets > 0:
            equity_ratio = total_equity / total_assets
            metrics['equity_ratio'] = round(equity_ratio, 2)
            
            if equity_ratio > 0.7:
                metrics['equity_ratio_health'] = 'Strong Equity Base'
            elif equity_ratio > 0.5:
                metrics['equity_ratio_health'] = 'Healthy'
            else:
                metrics['equity_ratio_health'] = 'Weak Equity Base'
        
        # ====================================
        # 3. WORKING CAPITAL ANALYSIS
        # ====================================
        
        if current_assets and current_liabilities:
            working_capital = current_assets - current_liabilities
            metrics['working_capital'] = working_capital
            
            # Working capital ratio
            if total_assets and total_assets > 0:
                wc_ratio = working_capital / total_assets
                metrics['working_capital_ratio'] = round(wc_ratio * 100, 2)
        
        # Net Working Capital Trend (if multiple years available)
        if len(balance_sheet.columns) >= 2 and current_assets is not None and current_liabilities is not None:
            wc_current = current_assets - current_liabilities
            
            # Previous year
            try:
                bs_prev = balance_sheet.iloc[:, 1]
                ca_prev = float(bs_prev.get(ca_key, 0)) if ca_key and ca_key in bs_prev.index else 0
                cl_prev = float(bs_prev.get(cl_key, 0)) if cl_key and cl_key in bs_prev.index else 0
                # Handle NaN values
                ca_prev = 0 if pd.isna(ca_prev) else ca_prev
                cl_prev = 0 if pd.isna(cl_prev) else cl_prev
                wc_prev = ca_prev - cl_prev
            except Exception:
                wc_prev = 0
            
            if wc_prev > 0:
                wc_change = ((wc_current - wc_prev) / wc_prev) * 100
                metrics['working_capital_change'] = round(wc_change, 2)
                
                if wc_change > 10:
                    metrics['wc_trend'] = 'Improving'
                elif wc_change > -10:
                    metrics['wc_trend'] = 'Stable'
                else:
                    metrics['wc_trend'] = 'Deteriorating'
        
        # ====================================
        # 4. ASSET QUALITY
        # ====================================
        
        # Tangible Book Value
        goodwill = 0
        intangibles = 0
        for key in ['Goodwill', 'GoodwillAndOtherIntangibleAssets']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    goodwill = float(val)
                    break
        for key in ['Intangible Assets', 'IntangibleAssets', 'OtherIntangibleAssets']:
            if key in balance_sheet.index:
                val = bs.get(key)
                if val is not None and not pd.isna(val):
                    intangibles = float(val)
                    break
        
        if total_equity:
            tangible_equity = total_equity - goodwill - intangibles
            metrics['tangible_book_value'] = tangible_equity
            
            # Tangible Asset Ratio
            if total_assets and total_assets > 0:
                tangible_ratio = tangible_equity / total_assets
                metrics['tangible_asset_ratio'] = round(tangible_ratio, 2)
                
                if tangible_ratio > 0.5:
                    metrics['asset_quality'] = 'High Quality (Tangible)'
                elif tangible_ratio > 0.3:
                    metrics['asset_quality'] = 'Good Quality'
                else:
                    metrics['asset_quality'] = 'Intangible-Heavy'
        
        # ====================================
        # 5. INTEREST COVERAGE (from income statement)
        # ====================================
        
        if not income_stmt.empty:
            inc = income_stmt.iloc[:, 0]
            
            ebit = None
            interest = None
            
            for key in ['EBIT', 'Operating Income', 'OperatingIncome', 'Operating_Income']:
                if key in income_stmt.index:
                    val = inc.get(key)
                    if val is not None and not pd.isna(val):
                        ebit = float(val)
                        break
            
            for key in ['Interest Expense', 'Interest Expense Non Operating', 'InterestExpense']:
                if key in income_stmt.index:
                    val = inc.get(key)
                    if val is not None and not pd.isna(val):
                        interest = abs(float(val))  # Usually negative
                        break
            
            if ebit is not None and interest is not None and interest > 0:
                interest_coverage = ebit / interest
                metrics['interest_coverage'] = round(interest_coverage, 2)
                
                if interest_coverage > 10:
                    metrics['interest_coverage_health'] = 'Excellent'
                elif interest_coverage > 5:
                    metrics['interest_coverage_health'] = 'Good'
                elif interest_coverage > 2.5:
                    metrics['interest_coverage_health'] = 'Adequate'
                elif interest_coverage > 1.5:
                    metrics['interest_coverage_health'] = 'Weak'
                else:
                    metrics['interest_coverage_health'] = 'At Risk'
        
        # ====================================
        # 6. BALANCE SHEET HEALTH SCORE
        # ====================================
        
        score = 0
        max_score = 0
        
        # Liquidity (30 points)
        if 'current_ratio' in metrics:
            max_score += 10
            cr = metrics['current_ratio']
            if cr >= 2:
                score += 10
            elif cr >= 1.5:
                score += 8
            elif cr >= 1:
                score += 5
            else:
                score += 2
        
        if 'quick_ratio' in metrics:
            max_score += 10
            qr = metrics['quick_ratio']
            if qr >= 1.5:
                score += 10
            elif qr >= 1:
                score += 8
            elif qr >= 0.5:
                score += 5
            else:
                score += 2
        
        if 'cash_ratio' in metrics:
            max_score += 10
            cr = metrics['cash_ratio']
            if cr >= 0.5:
                score += 10
            elif cr >= 0.3:
                score += 7
            elif cr >= 0.1:
                score += 4
            else:
                score += 1
        
        # Leverage (40 points)
        if 'debt_to_equity' in metrics:
            max_score += 20
            dte = metrics['debt_to_equity']
            if dte < 0.3:
                score += 20
            elif dte < 0.5:
                score += 17
            elif dte < 1:
                score += 12
            elif dte < 2:
                score += 7
            else:
                score += 2
        
        if 'interest_coverage' in metrics:
            max_score += 20
            ic = metrics['interest_coverage']
            if ic > 10:
                score += 20
            elif ic > 5:
                score += 15
            elif ic > 2.5:
                score += 10
            elif ic > 1.5:
                score += 5
            else:
                score += 1
        
        # Asset Quality (30 points)
        if 'tangible_asset_ratio' in metrics:
            max_score += 15
            tar = metrics['tangible_asset_ratio']
            if tar > 0.5:
                score += 15
            elif tar > 0.3:
                score += 10
            else:
                score += 5
        
        if 'working_capital_ratio' in metrics:
            max_score += 15
            wcr = metrics['working_capital_ratio']
            if wcr > 20:
                score += 15
            elif wcr > 10:
                score += 10
            elif wcr > 0:
                score += 5
            else:
                score += 0
        
        if max_score > 0:
            metrics['balance_sheet_score'] = round((score / max_score) * 100, 2)
            
            if metrics['balance_sheet_score'] >= 80:
                metrics['balance_sheet_rating'] = 'Fortress (Excellent)'
            elif metrics['balance_sheet_score'] >= 60:
                metrics['balance_sheet_rating'] = 'Strong'
            elif metrics['balance_sheet_score'] >= 40:
                metrics['balance_sheet_rating'] = 'Adequate'
            else:
                metrics['balance_sheet_rating'] = 'Weak'
        
        print(f"[OK] Balance sheet analysis complete")
        print(f"     Current Ratio: {metrics.get('current_ratio', 'N/A')}")
        print(f"     D/E Ratio: {metrics.get('debt_to_equity', 'N/A')}")
        print(f"     Score: {metrics.get('balance_sheet_score', 0)}/100")
        
        return {
            'status': 'success',
            'metrics': metrics
        }
        
    except Exception as e:
        print(f"[ERROR] Balance sheet analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error analyzing balance sheet: {str(e)}'
        }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING BALANCE SHEET HEALTH MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    print(f"\n[TEST] Balance Sheet Analysis for {test_ticker}")
    print("-"*80)
    bs_data = analyze_balance_sheet_health(test_ticker)
    
    if bs_data['status'] == 'success':
        metrics = bs_data['metrics']
        
        print(f"\nLiquidity Ratios:")
        print(f"  Current Ratio: {metrics.get('current_ratio', 'N/A')} - {metrics.get('current_ratio_health', 'N/A')}")
        print(f"  Quick Ratio: {metrics.get('quick_ratio', 'N/A')} - {metrics.get('quick_ratio_health', 'N/A')}")
        print(f"  Cash Ratio: {metrics.get('cash_ratio', 'N/A')} - {metrics.get('cash_ratio_health', 'N/A')}")
        
        print(f"\nLeverage Ratios:")
        print(f"  Debt/Equity: {metrics.get('debt_to_equity', 'N/A')} - {metrics.get('debt_to_equity_health', 'N/A')}")
        print(f"  Debt/Assets: {metrics.get('debt_to_assets', 'N/A')} - {metrics.get('debt_to_assets_health', 'N/A')}")
        print(f"  Equity Ratio: {metrics.get('equity_ratio', 'N/A')} - {metrics.get('equity_ratio_health', 'N/A')}")
        
        print(f"\nWorking Capital:")
        if 'working_capital' in metrics:
            wc = metrics['working_capital'] / 1e9
            print(f"  Working Capital: ${wc:.2f}B")
        print(f"  WC Ratio: {metrics.get('working_capital_ratio', 'N/A')}%")
        print(f"  WC Trend: {metrics.get('wc_trend', 'N/A')}")
        
        print(f"\nAsset Quality:")
        print(f"  Tangible Asset Ratio: {metrics.get('tangible_asset_ratio', 'N/A')}")
        print(f"  Quality: {metrics.get('asset_quality', 'N/A')}")
        
        print(f"\nDebt Servicing:")
        print(f"  Interest Coverage: {metrics.get('interest_coverage', 'N/A')}x")
        print(f"  Health: {metrics.get('interest_coverage_health', 'N/A')}")
        
        print(f"\nOverall Score:")
        print(f"  Balance Sheet Score: {metrics.get('balance_sheet_score', 0)}/100")
        print(f"  Rating: {metrics.get('balance_sheet_rating', 'N/A')}")
        
        print("\n[OK] Test PASSED")
    else:
        print(f"\n[FAIL] {bs_data['message']}")
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
    print(f"\nTotal Metrics Delivered: ~20")
    print(f"Liquidity, Leverage, Working Capital, Asset Quality, Coverage")

