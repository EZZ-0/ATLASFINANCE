"""
CORPORATE GOVERNANCE MODULE
================================================================================
Comprehensive governance, capital structure, and shareholder analysis.

Based on ISS (Institutional Shareholder Services) methodology and 
academic best practices for governance assessment.

Features:
- Board of Directors composition & independence
- Atlas Governance Score (AGS) - Similar to ISS methodology
- Equity structure & share classes
- Top shareholders & insider ownership
- Capital structure (debt/equity)
- SEC filing links (Proxy, 10-K, 8-K)
- Investor Relations links
- Overall governance assessment

Data Sources: Yahoo Finance, SEC Edgar (via links)
Author: Atlas Financial Intelligence
Date: November 2025
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests
from typing import Dict, List, Optional
import streamlit as st

# Import centralized cache to prevent Yahoo rate limiting
from utils.ticker_cache import get_ticker_info, get_ticker


@st.cache_data(ttl=86400)  # Cache for 24 hours (governance changes slowly)
def analyze_governance(ticker: str) -> Dict:
    """
    Comprehensive governance analysis
    
    Returns dictionary with:
    - Board composition
    - Governance scores (Atlas Governance Score)
    - Equity structure
    - Capital structure
    - Shareholder info
    - SEC filing links
    """
    
    try:
        # Use centralized cache to prevent Yahoo rate limiting
        info = get_ticker_info(ticker)
        stock = get_ticker(ticker)
        
        results = {
            'status': 'success',
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
        }
        
        # ==========================================
        # A. BOARD OF DIRECTORS
        # ==========================================
        
        board_data = {
            'total_directors': None,
            'independent_directors': None,
            'insider_directors': None,
            'independence_ratio': None,
            'board_size_assessment': None,
            'estimated': True,  # Flag that some data is estimated
            'officers': [],  # List of company officers/directors
        }
        
        # Get company officers from Yahoo Finance
        try:
            officers = info.get('companyOfficers', [])
            if officers:
                board_data['officers'] = [
                    {
                        'name': officer.get('name', 'N/A'),
                        'title': officer.get('title', 'N/A'),
                        'age': officer.get('age'),
                        'totalPay': officer.get('totalPay'),
                        'exercisedValue': officer.get('exercisedValue'),
                        'unexercisedValue': officer.get('unexercisedValue'),
                    }
                    for officer in officers
                ]
        except Exception:
            pass
        
        # Get from Yahoo Finance info
        board_size = info.get('boardSize')
        if board_size:
            board_data['total_directors'] = board_size
            
            # Estimate independence (industry average ~80%)
            # NOTE: Exact data requires proxy statement parsing
            estimated_independent = int(board_size * 0.8)
            board_data['independent_directors'] = estimated_independent
            board_data['insider_directors'] = board_size - estimated_independent
            board_data['independence_ratio'] = estimated_independent / board_size
            
            # Assess board size (best practice: 7-12 members)
            if board_size < 5:
                board_data['board_size_assessment'] = 'Too Small'
                board_data['board_risk'] = 'Risk: Lack of expertise diversity'
            elif 7 <= board_size <= 12:
                board_data['board_size_assessment'] = 'Optimal'
                board_data['board_risk'] = 'Best practice range (7-12 members)'
            elif board_size <= 15:
                board_data['board_size_assessment'] = 'Acceptable'
                board_data['board_risk'] = 'Slightly large but manageable'
            else:
                board_data['board_size_assessment'] = 'Too Large'
                board_data['board_risk'] = 'Risk: Slower decision-making'
        
        results['board'] = board_data
        
        # ==========================================
        # B. ATLAS GOVERNANCE SCORE (AGS)
        # ==========================================
        
        governance_score = calculate_governance_score(info, stock)
        results['governance_score'] = governance_score
        
        # ==========================================
        # C. EQUITY STRUCTURE
        # ==========================================
        
        equity_data = {
            'shares_outstanding': info.get('sharesOutstanding'),
            'float_shares': info.get('floatShares'),
            'free_float_ratio': None,
            'shares_short': info.get('sharesShort'),
            'short_ratio': info.get('shortRatio'),
            'short_percent_of_float': info.get('shortPercentOfFloat'),
            'insider_ownership_pct': info.get('heldPercentInsiders'),
            'institutional_ownership_pct': info.get('heldPercentInstitutions'),
            'liquidity_assessment': None,
        }
        
        # Calculate free float ratio
        if equity_data['float_shares'] and equity_data['shares_outstanding']:
            equity_data['free_float_ratio'] = equity_data['float_shares'] / equity_data['shares_outstanding']
        
        # Assess liquidity
        if equity_data['free_float_ratio']:
            if equity_data['free_float_ratio'] > 0.8:
                equity_data['liquidity_assessment'] = 'High (Widely traded)'
            elif equity_data['free_float_ratio'] > 0.5:
                equity_data['liquidity_assessment'] = 'Moderate'
            else:
                equity_data['liquidity_assessment'] = 'Low (Concentrated ownership)'
        
        results['equity_structure'] = equity_data
        
        # ==========================================
        # D. CAPITAL STRUCTURE
        # ==========================================
        
        capital_data = {
            'total_debt': info.get('totalDebt'),
            'total_cash': info.get('totalCash'),
            'net_debt': None,
            'total_equity': info.get('totalStockholderEquity'),
            'debt_to_equity': None,
            'debt_to_capital': None,
            'interest_coverage': None,
            'leverage_assessment': None,
        }
        
        # Calculate net debt
        if capital_data['total_debt'] and capital_data['total_cash']:
            capital_data['net_debt'] = capital_data['total_debt'] - capital_data['total_cash']
        
        # Calculate debt ratios
        if capital_data['total_debt'] and capital_data['total_equity'] and capital_data['total_equity'] > 0:
            capital_data['debt_to_equity'] = capital_data['total_debt'] / capital_data['total_equity']
            
            total_capital = capital_data['total_debt'] + capital_data['total_equity']
            capital_data['debt_to_capital'] = capital_data['total_debt'] / total_capital if total_capital > 0 else None
        
        # Interest coverage (EBIT / Interest Expense)
        ebit = info.get('ebit')
        interest_expense = info.get('interestExpense')
        if ebit and interest_expense and interest_expense != 0:
            capital_data['interest_coverage'] = ebit / abs(interest_expense)
        
        # Assess leverage
        if capital_data['debt_to_equity'] is not None:
            if capital_data['debt_to_equity'] < 0.3:
                capital_data['leverage_assessment'] = 'Conservative'
                capital_data['leverage_note'] = 'Low debt - strong financial flexibility'
            elif capital_data['debt_to_equity'] < 1.0:
                capital_data['leverage_assessment'] = 'Moderate'
                capital_data['leverage_note'] = 'Balanced capital structure'
            elif capital_data['debt_to_equity'] < 2.0:
                capital_data['leverage_assessment'] = 'High'
                capital_data['leverage_note'] = 'Elevated leverage - monitor closely'
            else:
                capital_data['leverage_assessment'] = 'Very High'
                capital_data['leverage_note'] = 'Significant financial risk'
        
        results['capital_structure'] = capital_data
        
        # ==========================================
        # E. TOP SHAREHOLDERS
        # ==========================================
        
        # Get institutional holders
        institutional_holders = stock.institutional_holders
        major_holders = stock.major_holders
        
        if institutional_holders is not None and not institutional_holders.empty:
            top_holders = []
            for idx, row in institutional_holders.head(10).iterrows():
                top_holders.append({
                    'holder': row.get('Holder', 'N/A'),
                    'shares': row.get('Shares', 0),
                    'date_reported': str(row.get('Date Reported', 'N/A')),
                    'percent_out': row.get('% Out', row.get('Pct Out', 0)),
                    'value': row.get('Value', 0),
                })
            results['top_shareholders'] = top_holders
        else:
            results['top_shareholders'] = []
        
        # Parse major holders summary
        if major_holders is not None and not major_holders.empty:
            major_holders_dict = {}
            try:
                for idx, row in major_holders.iterrows():
                    # Check if row has at least 2 columns
                    if len(row) >= 2:
                        major_holders_dict[row[0]] = row[1]
                    elif len(row) == 1:
                        # Single column, use index as key
                        major_holders_dict[str(idx)] = row[0]
            except Exception as e:
                # If parsing fails, just skip
                pass
            results['major_holders_summary'] = major_holders_dict
        else:
            results['major_holders_summary'] = {}
        
        # ==========================================
        # F. SEC FILING LINKS
        # ==========================================
        
        sec_links = get_sec_filing_links(ticker)
        results['sec_links'] = sec_links
        
        # ==========================================
        # G. SHAREHOLDER RIGHTS
        # ==========================================
        
        rights_data = {
            'dual_class_shares': check_dual_class(info, ticker),
            'dual_class_note': None,
        }
        
        if rights_data['dual_class_shares']:
            rights_data['dual_class_note'] = 'Company has dual-class share structure which may limit shareholder voting power'
        
        results['shareholder_rights'] = rights_data
        
        # ==========================================
        # H. OVERALL ASSESSMENT
        # ==========================================
        
        assessment = generate_governance_assessment(results)
        results['overall_assessment'] = assessment
        
        return results
        
    except Exception as e:
        print(f"[ERROR] Governance analysis failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error analyzing governance: {str(e)}'
        }


def calculate_governance_score(info: Dict, stock) -> Dict:
    """
    Calculate Atlas Governance Score (AGS) - Similar to ISS methodology
    
    Score: 1-10 (lower is better, like ISS QualityScore)
    Grade: A-F letter grade
    
    Based on 4 pillars:
    1. Board Structure (40% weight)
    2. Compensation (25% weight)
    3. Shareholder Rights (20% weight)
    4. Audit & Risk Oversight (15% weight)
    """
    
    score_data = {
        'overall_score': None,
        'board_score': None,
        'compensation_score': None,
        'shareholder_rights_score': None,
        'audit_score': None,
        'overall_grade': None,
        'risk_level': None,
        'interpretation': None,
        'methodology_note': 'Atlas Governance Score (AGS) uses similar methodology to ISS QualityScore but with publicly available data. This is not an official ISS score.',
    }
    
    scores = []
    
    # ==========================================
    # 1. BOARD STRUCTURE SCORE (40% weight)
    # ==========================================
    board_size = info.get('boardSize')
    if board_size:
        board_score = 5  # Start with neutral (1-10 scale)
        
        # Optimal size: 7-12 members
        if 7 <= board_size <= 12:
            board_score -= 2  # Good (score goes down)
        elif board_size < 5:
            board_score += 3  # Too small (score goes up = worse)
        elif board_size > 15:
            board_score += 2  # Too large
        
        # Assume 80% independence (would need proxy statement for exact)
        # Good governance: >75% independent
        # This adds nothing to score (neutral assumption)
        
        scores.append(('board', board_score, 0.40))
        score_data['board_score'] = board_score
    
    # ==========================================
    # 2. COMPENSATION SCORE (25% weight)
    # ==========================================
    # Check pay-for-performance alignment
    # (Simplified - full analysis needs proxy DEF 14A)
    compensation_score = 5  # Neutral default
    
    # Could add checks for:
    # - CEO pay ratio
    # - Pay vs performance correlation
    # But requires more data than Yahoo provides
    
    scores.append(('compensation', compensation_score, 0.25))
    score_data['compensation_score'] = compensation_score
    
    # ==========================================
    # 3. SHAREHOLDER RIGHTS SCORE (20% weight)
    # ==========================================
    rights_score = 5  # Neutral default
    
    # Check for dual-class shares (bad for governance)
    if check_dual_class(info, info.get('symbol', '')):
        rights_score += 3  # Penalty for dual-class structure
    
    # Check insider ownership (sweet spot: 1-30%)
    insider_pct = info.get('heldPercentInsiders', 0)
    if insider_pct > 0.50:
        rights_score += 2  # Too high = entrenchment risk
    elif insider_pct < 0.01:
        rights_score += 1  # Too low = alignment risk
    
    scores.append(('shareholder_rights', rights_score, 0.20))
    score_data['shareholder_rights_score'] = rights_score
    
    # ==========================================
    # 4. AUDIT & RISK SCORE (15% weight)
    # ==========================================
    audit_score = 5  # Neutral default
    
    # Check for red flags in financials
    # (Would need more data from proxy statements for full assessment)
    
    scores.append(('audit', audit_score, 0.15))
    score_data['audit_score'] = audit_score
    
    # ==========================================
    # CALCULATE OVERALL SCORE
    # ==========================================
    if scores:
        overall = sum(score * weight for _, score, weight in scores)
        score_data['overall_score'] = round(overall, 1)
        
        # Convert to letter grade
        if overall <= 2:
            score_data['overall_grade'] = 'A'
            score_data['grade_interpretation'] = 'Excellent'
        elif overall <= 3:
            score_data['overall_grade'] = 'A-'
            score_data['grade_interpretation'] = 'Very Good'
        elif overall <= 4:
            score_data['overall_grade'] = 'B'
            score_data['grade_interpretation'] = 'Good'
        elif overall <= 5:
            score_data['overall_grade'] = 'B-'
            score_data['grade_interpretation'] = 'Acceptable'
        elif overall <= 6:
            score_data['overall_grade'] = 'C'
            score_data['grade_interpretation'] = 'Fair'
        elif overall <= 7:
            score_data['overall_grade'] = 'D'
            score_data['grade_interpretation'] = 'Concerns'
        else:
            score_data['overall_grade'] = 'F'
            score_data['grade_interpretation'] = 'Poor'
        
        # Risk level assessment (ISS style)
        if overall <= 3:
            score_data['risk_level'] = 'Low Risk'
            score_data['interpretation'] = 'Strong governance practices'
        elif overall <= 5:
            score_data['risk_level'] = 'Moderate Risk'
            score_data['interpretation'] = 'Acceptable governance with room for improvement'
        elif overall <= 7:
            score_data['risk_level'] = 'Elevated Risk'
            score_data['interpretation'] = 'Some governance concerns identified'
        else:
            score_data['risk_level'] = 'High Risk'
            score_data['interpretation'] = 'Significant governance issues'
    
    return score_data


def check_dual_class(info: Dict, ticker: str) -> bool:
    """
    Check if company has dual-class share structure
    
    Indicators:
    - Multiple share classes in name
    - Class A/B/C in ticker
    - Voting rights disparity
    """
    company_name = info.get('longName', '')
    
    # Common dual-class indicators
    dual_class_patterns = ['Class A', 'Class B', 'Class C', 'Ordinary Shares', 'Super Voting']
    
    # Check company name
    for pattern in dual_class_patterns:
        if pattern in company_name:
            return True
    
    # Check ticker for .A, .B suffixes or GOOGL vs GOOG pattern
    if ticker.endswith('.A') or ticker.endswith('.B') or ticker.endswith('.C'):
        return True
    
    # Known dual-class companies
    known_dual_class = ['GOOGL', 'GOOG', 'BRK.A', 'BRK.B', 'FB', 'META', 'SNAP', 'LYFT']
    if ticker in known_dual_class:
        return True
    
    return False


def get_sec_filing_links(ticker: str) -> Dict:
    """
    Generate direct links to SEC Edgar filings
    
    Returns links to:
    - Proxy Statement (DEF 14A) - Board composition, compensation
    - Annual Report (10-K) - Capital structure, risk factors
    - Current Reports (8-K) - Material events
    - All filings
    - Investor Relations page (if available)
    """
    
    links = {
        'status': 'success',
        'cik': None,
        'proxy_statement': None,
        'annual_report': None,
        'current_reports': None,
        'all_filings': None,
        'investor_relations': None,
        'investor_relations_note': None,
    }
    
    # Get CIK (Central Index Key)
    cik = get_cik(ticker)
    
    if cik:
        links['cik'] = cik
        
        # SEC Edgar base URL
        base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        
        # Generate filing URLs
        links['proxy_statement'] = f"{base_url}?action=getcompany&CIK={cik}&type=DEF%2014A&dateb=&owner=exclude&count=10"
        links['annual_report'] = f"{base_url}?action=getcompany&CIK={cik}&type=10-K&dateb=&owner=exclude&count=10"
        links['current_reports'] = f"{base_url}?action=getcompany&CIK={cik}&type=8-K&dateb=&owner=exclude&count=40"
        links['all_filings'] = f"{base_url}?action=getcompany&CIK={cik}&owner=exclude&count=100"
    
    # Try to get Investor Relations page
    try:
        # Use centralized cache to prevent Yahoo rate limiting
        info = get_ticker_info(ticker)
        
        # Priority 1: Use yfinance's dedicated IR website if available (most accurate)
        if 'irWebsite' in info and info['irWebsite']:
            links['investor_relations'] = info['irWebsite']
        # Priority 2: Use main website with helpful note
        elif 'website' in info and info['website']:
            website = info['website']
            links['investor_relations'] = website
            links['investor_relations_note'] = "Main website - look for 'Investors' or 'IR' section"
        
    except:
        pass
    
    return links


def get_cik(ticker: str) -> Optional[str]:
    """
    Get CIK (Central Index Key) for a ticker from SEC
    
    Multi-tier approach:
    1. Check local hardcoded dictionary (S&P 500 + popular stocks)
    2. Query SEC API (requires proper User-Agent)
    3. Fallback to yfinance
    
    ⚠️ PRIORITY FIX REQUIRED:
    - Replace placeholder email: contact@placeholder.com
    - Register with SEC: https://www.sec.gov/os/accessing-edgar-data
    - Update User-Agent with real contact information
    - SEC Fair Access Policy requires declared identity (FREE, no cost)
    """
    
    ticker_upper = ticker.upper().strip()
    
    # ==========================================
    # TIER 1: Local Hardcoded CIKs (Instant)
    # ==========================================
    try:
        from sp500_ciks import get_cik_from_local
        local_cik = get_cik_from_local(ticker_upper)
        if local_cik:
            return local_cik
    except Exception:
        pass
    
    # ==========================================
    # TIER 2: SEC API (Free, requires registration)
    # ==========================================
    try:
        url = "https://www.sec.gov/files/company_tickers.json"
        
        # TODO: Replace with real email after SEC registration
        headers = {
            'User-Agent': 'AtlasFinancialIntelligence/1.0 (Atlasfinancialintel@gmail.com)',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Search for ticker
            for item in data.values():
                if item.get('ticker', '').upper().strip() == ticker_upper:
                    # CIK must be 10 digits, padded with zeros
                    cik = str(item['cik_str']).zfill(10)
                    return cik
        
        elif response.status_code == 403:
            # SEC blocking - need proper User-Agent registration
            pass
        
    except (requests.Timeout, requests.ConnectionError):
        pass
    except Exception:
        pass
    
    # ==========================================
    # TIER 3: YFinance Fallback
    # ==========================================
    try:
        # Use centralized cache to prevent Yahoo rate limiting
        info = get_ticker_info(ticker)
        
        if 'cik' in info:
            return str(info['cik']).zfill(10)
    except Exception:
        pass
    
    # No CIK found
    return None


def generate_governance_assessment(results: Dict) -> Dict:
    """
    Generate overall governance assessment with strengths, concerns, and recommendations
    """
    
    strengths = []
    concerns = []
    recommendations = []
    
    # ==========================================
    # BOARD ANALYSIS
    # ==========================================
    board = results.get('board', {})
    
    if board.get('independence_ratio'):
        if board['independence_ratio'] >= 0.75:
            strengths.append(f"Strong board independence (~{board['independence_ratio']:.0%})")
        elif board['independence_ratio'] < 0.60:
            concerns.append(f"Low board independence (~{board['independence_ratio']:.0%})")
    
    if board.get('board_size_assessment'):
        if board['board_size_assessment'] == 'Optimal':
            strengths.append(f"Optimal board size ({board['total_directors']} members)")
        elif board['board_size_assessment'] in ['Too Small', 'Too Large']:
            concerns.append(f"{board['board_size_assessment']} board size ({board['total_directors']} members)")
    
    # ==========================================
    # OWNERSHIP ANALYSIS
    # ==========================================
    equity = results.get('equity_structure', {})
    
    insider_pct = equity.get('insider_ownership_pct', 0)
    if insider_pct:
        if 0.01 <= insider_pct <= 0.30:
            strengths.append(f"Healthy insider ownership ({insider_pct:.1%}) - Good alignment")
        elif insider_pct > 0.50:
            concerns.append(f"High insider ownership ({insider_pct:.1%}) - Potential entrenchment")
    
    institutional_pct = equity.get('institutional_ownership_pct', 0)
    if institutional_pct and institutional_pct > 0.60:
        strengths.append(f"Strong institutional ownership ({institutional_pct:.1%}) - Professional oversight")
    
    free_float = equity.get('free_float_ratio')
    if free_float and free_float > 0.70:
        strengths.append(f"High free float ({free_float:.1%}) - Good liquidity")
    elif free_float and free_float < 0.30:
        concerns.append(f"Low free float ({free_float:.1%}) - Limited liquidity")
    
    # ==========================================
    # CAPITAL STRUCTURE ANALYSIS
    # ==========================================
    capital = results.get('capital_structure', {})
    
    if capital.get('leverage_assessment'):
        if capital['leverage_assessment'] in ['Conservative', 'Moderate']:
            strengths.append(f"{capital['leverage_assessment']} leverage - {capital.get('leverage_note', '')}")
        else:
            concerns.append(f"{capital['leverage_assessment']} leverage - {capital.get('leverage_note', '')}")
    
    interest_coverage = capital.get('interest_coverage')
    if interest_coverage:
        if interest_coverage > 5:
            strengths.append(f"Strong debt service coverage ({interest_coverage:.1f}x)")
        elif interest_coverage < 2:
            concerns.append(f"Weak debt service coverage ({interest_coverage:.1f}x)")
    
    # ==========================================
    # SHAREHOLDER RIGHTS
    # ==========================================
    rights = results.get('shareholder_rights', {})
    
    if rights.get('dual_class_shares'):
        concerns.append("Dual-class share structure may limit shareholder voting power")
        recommendations.append("Review proxy statement for voting rights details")
    
    # ==========================================
    # GENERATE RECOMMENDATIONS
    # ==========================================
    if not recommendations:
        recommendations.append("Review annual Proxy Statement (DEF 14A) for detailed governance practices")
        
        if len(concerns) > len(strengths):
            recommendations.append("Monitor shareholder proposals and voting results closely")
            recommendations.append("Consider governance improvements or shareholder activism")
        else:
            recommendations.append("Governance appears sound - continue annual monitoring")
    
    # ==========================================
    # CALCULATE OVERALL GRADE
    # ==========================================
    ratio = len(strengths) / max(len(concerns), 1)
    
    if ratio >= 3:
        overall_grade = 'A (Excellent)'
    elif ratio >= 2:
        overall_grade = 'B (Good)'
    elif ratio >= 1:
        overall_grade = 'C (Acceptable)'
    elif ratio >= 0.5:
        overall_grade = 'D (Concerns)'
    else:
        overall_grade = 'F (Poor)'
    
    return {
        'strengths': strengths,
        'concerns': concerns,
        'recommendations': recommendations,
        'overall_grade': overall_grade,
        'strength_count': len(strengths),
        'concern_count': len(concerns),
    }


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING GOVERNANCE ANALYSIS MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    print(f"\n[TEST] Governance Analysis for {test_ticker}")
    print("-"*80)
    
    gov_data = analyze_governance(test_ticker)
    
    if gov_data['status'] == 'success':
        print(f"\n✅ Company: {gov_data['company_name']}")
        
        # Board
        board = gov_data.get('board', {})
        if board.get('total_directors'):
            print(f"\nBoard of Directors:")
            print(f"  Total Members: {board['total_directors']}")
            print(f"  Independent: ~{board['independent_directors']} ({board['independence_ratio']:.0%})")
            print(f"  Assessment: {board['board_size_assessment']}")
        
        # Governance Score
        score = gov_data.get('governance_score', {})
        print(f"\nAtlas Governance Score:")
        print(f"  Overall: {score.get('overall_score', 'N/A')}/10")
        print(f"  Grade: {score.get('overall_grade', 'N/A')}")
        print(f"  Risk Level: {score.get('risk_level', 'N/A')}")
        
        # Capital Structure
        capital = gov_data.get('capital_structure', {})
        if capital.get('debt_to_equity') is not None:
            print(f"\nCapital Structure:")
            print(f"  Debt/Equity: {capital['debt_to_equity']:.2f}")
            print(f"  Assessment: {capital.get('leverage_assessment', 'N/A')}")
        
        # SEC Links
        sec = gov_data.get('sec_links', {})
        if sec.get('cik'):
            print(f"\nSEC Edgar:")
            print(f"  CIK: {sec['cik']}")
            print(f"  Proxy: Available")
            print(f"  10-K: Available")
        
        # Assessment
        assessment = gov_data.get('overall_assessment', {})
        print(f"\nOverall Assessment:")
        print(f"  Strengths: {assessment['strength_count']}")
        print(f"  Concerns: {assessment['concern_count']}")
        print(f"  Grade: {assessment['overall_grade']}")
        
        print("\n[OK] Test PASSED")
    else:
        print(f"\n[FAIL] {gov_data['message']}")
    
    print("\n" + "="*80)

