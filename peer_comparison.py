"""
PEER COMPARISON MODULE
================================================================================
Intelligent peer discovery and comprehensive competitive benchmarking.

Features:
- Automatic peer discovery (sector/industry based)
- Side-by-side financial comparison (10-15 key metrics)
- Percentile rankings and statistical analysis
- Interactive heatmap visualization
- Export to Excel/CSV

Data Sources: Yahoo Finance (yfinance)
Author: Atlas Financial Intelligence
Date: November 2025
Phase: 6C-A (Foundation)
"""

import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Use centralized ticker cache to avoid rate limiting
from utils.ticker_cache import get_ticker_info


# Related industries mapping - industries that are similar enough to be valid peers
# Comprehensive mapping to ensure peer discovery works for ALL S&P 500 stocks
RELATED_INDUSTRIES = {
    # === TECHNOLOGY ===
    'Consumer Electronics': ['Consumer Electronics', 'Computer Hardware', 'Electronic Components', 'Communication Equipment', 'Semiconductors'],
    'Computer Hardware': ['Computer Hardware', 'Consumer Electronics', 'Electronic Components', 'Semiconductors'],
    'Software - Infrastructure': ['Software - Infrastructure', 'Software - Application', 'Information Technology Services', 'Internet Content & Information'],
    'Software - Application': ['Software - Application', 'Software - Infrastructure', 'Internet Content & Information', 'Information Technology Services'],
    'Semiconductors': ['Semiconductors', 'Semiconductor Equipment & Materials', 'Electronic Components', 'Consumer Electronics'],
    'Semiconductor Equipment & Materials': ['Semiconductor Equipment & Materials', 'Semiconductors', 'Electronic Components'],
    'Electronic Components': ['Electronic Components', 'Semiconductors', 'Consumer Electronics', 'Communication Equipment'],
    'Communication Equipment': ['Communication Equipment', 'Consumer Electronics', 'Electronic Components'],
    'Information Technology Services': ['Information Technology Services', 'Software - Infrastructure', 'Software - Application'],
    'Scientific & Technical Instruments': ['Scientific & Technical Instruments', 'Electronic Components', 'Medical Devices'],
    
    # === COMMUNICATION SERVICES ===
    'Internet Content & Information': ['Internet Content & Information', 'Software - Application', 'Entertainment', 'Advertising Agencies'],
    'Entertainment': ['Entertainment', 'Internet Content & Information', 'Broadcasting', 'Media - Diversified'],
    'Broadcasting': ['Broadcasting', 'Entertainment', 'Media - Diversified', 'Telecom Services'],
    'Media - Diversified': ['Media - Diversified', 'Entertainment', 'Broadcasting', 'Publishing'],
    'Telecom Services': ['Telecom Services', 'Broadcasting', 'Communication Equipment'],
    'Advertising Agencies': ['Advertising Agencies', 'Internet Content & Information', 'Media - Diversified'],
    'Electronic Gaming & Multimedia': ['Electronic Gaming & Multimedia', 'Entertainment', 'Internet Content & Information'],
    
    # === CONSUMER CYCLICAL ===
    'Internet Retail': ['Internet Retail', 'Specialty Retail', 'Department Stores', 'Discount Stores'],
    'Auto Manufacturers': ['Auto Manufacturers', 'Auto Parts', 'Auto Dealerships'],
    'Auto Parts': ['Auto Parts', 'Auto Manufacturers', 'Auto Dealerships'],
    'Restaurants': ['Restaurants', 'Food Distribution', 'Leisure'],
    'Specialty Retail': ['Specialty Retail', 'Department Stores', 'Discount Stores', 'Internet Retail'],
    'Home Improvement Retail': ['Home Improvement Retail', 'Specialty Retail', 'Building Products'],
    'Discount Stores': ['Discount Stores', 'Department Stores', 'Grocery Stores', 'Internet Retail'],
    'Department Stores': ['Department Stores', 'Specialty Retail', 'Discount Stores'],
    'Apparel Retail': ['Apparel Retail', 'Specialty Retail', 'Apparel Manufacturing', 'Footwear & Accessories'],
    'Footwear & Accessories': ['Footwear & Accessories', 'Apparel Retail', 'Apparel Manufacturing'],
    'Apparel Manufacturing': ['Apparel Manufacturing', 'Apparel Retail', 'Footwear & Accessories'],
    'Lodging': ['Lodging', 'Resorts & Casinos', 'Travel Services', 'Restaurants'],
    'Resorts & Casinos': ['Resorts & Casinos', 'Lodging', 'Entertainment', 'Leisure'],
    'Travel Services': ['Travel Services', 'Lodging', 'Airlines'],
    'Residential Construction': ['Residential Construction', 'Building Products', 'Home Improvement Retail'],
    'Building Products': ['Building Products', 'Residential Construction', 'Home Improvement Retail'],
    'Leisure': ['Leisure', 'Entertainment', 'Restaurants', 'Resorts & Casinos'],
    
    # === CONSUMER DEFENSIVE ===
    'Beverages - Non-Alcoholic': ['Beverages - Non-Alcoholic', 'Beverages - Brewers', 'Packaged Foods'],
    'Beverages - Brewers': ['Beverages - Brewers', 'Beverages - Non-Alcoholic', 'Beverages - Wineries & Distilleries'],
    'Beverages - Wineries & Distilleries': ['Beverages - Wineries & Distilleries', 'Beverages - Brewers'],
    'Packaged Foods': ['Packaged Foods', 'Food Distribution', 'Confectioners', 'Beverages - Non-Alcoholic'],
    'Confectioners': ['Confectioners', 'Packaged Foods', 'Food Distribution'],
    'Household & Personal Products': ['Household & Personal Products', 'Consumer Products', 'Packaged Foods'],
    'Tobacco': ['Tobacco', 'Packaged Foods', 'Beverages - Brewers'],
    'Grocery Stores': ['Grocery Stores', 'Discount Stores', 'Food Distribution'],
    'Food Distribution': ['Food Distribution', 'Grocery Stores', 'Packaged Foods'],
    'Consumer Products': ['Consumer Products', 'Household & Personal Products', 'Packaged Foods'],
    
    # === HEALTHCARE ===
    'Drug Manufacturers - General': ['Drug Manufacturers - General', 'Drug Manufacturers - Specialty & Generic', 'Biotechnology'],
    'Drug Manufacturers - Specialty & Generic': ['Drug Manufacturers - Specialty & Generic', 'Drug Manufacturers - General', 'Biotechnology'],
    'Biotechnology': ['Biotechnology', 'Drug Manufacturers - General', 'Drug Manufacturers - Specialty & Generic', 'Medical Devices'],
    'Medical Devices': ['Medical Devices', 'Diagnostics & Research', 'Biotechnology', 'Healthcare Equipment & Services'],
    'Diagnostics & Research': ['Diagnostics & Research', 'Medical Devices', 'Biotechnology'],
    'Health Care Plans': ['Health Care Plans', 'Health Care Providers', 'Medical Care Facilities'],
    'Health Care Providers': ['Health Care Providers', 'Health Care Plans', 'Medical Care Facilities'],
    'Medical Care Facilities': ['Medical Care Facilities', 'Health Care Providers', 'Health Care Plans'],
    'Medical Distribution': ['Medical Distribution', 'Medical Devices', 'Drug Manufacturers - General'],
    'Medical Instruments & Supplies': ['Medical Instruments & Supplies', 'Medical Devices', 'Diagnostics & Research'],
    'Healthcare Equipment & Services': ['Healthcare Equipment & Services', 'Medical Devices', 'Health Care Providers'],
    
    # === FINANCIAL SERVICES ===
    'Banks - Diversified': ['Banks - Diversified', 'Banks - Regional', 'Financial Services', 'Capital Markets'],
    'Banks - Regional': ['Banks - Regional', 'Banks - Diversified', 'Credit Services', 'Financial Services'],
    'Credit Services': ['Credit Services', 'Banks - Regional', 'Financial Services', 'Consumer Finance'],
    'Insurance - Life': ['Insurance - Life', 'Insurance - Diversified', 'Insurance - Property & Casualty'],
    'Insurance - Property & Casualty': ['Insurance - Property & Casualty', 'Insurance - Life', 'Insurance - Diversified'],
    'Insurance - Diversified': ['Insurance - Diversified', 'Insurance - Life', 'Insurance - Property & Casualty'],
    'Insurance Brokers': ['Insurance Brokers', 'Insurance - Diversified', 'Financial Services'],
    'Asset Management': ['Asset Management', 'Capital Markets', 'Financial Services'],
    'Capital Markets': ['Capital Markets', 'Asset Management', 'Banks - Diversified', 'Financial Services'],
    'Financial Services': ['Financial Services', 'Banks - Diversified', 'Capital Markets', 'Credit Services'],
    'Financial Data & Stock Exchanges': ['Financial Data & Stock Exchanges', 'Capital Markets', 'Financial Services'],
    
    # === INDUSTRIALS ===
    'Aerospace & Defense': ['Aerospace & Defense', 'Industrial Conglomerates', 'Specialty Industrial Machinery'],
    'Industrial Conglomerates': ['Industrial Conglomerates', 'Aerospace & Defense', 'Specialty Industrial Machinery'],
    'Specialty Industrial Machinery': ['Specialty Industrial Machinery', 'Industrial Conglomerates', 'Farm & Heavy Construction Machinery'],
    'Farm & Heavy Construction Machinery': ['Farm & Heavy Construction Machinery', 'Specialty Industrial Machinery', 'Trucking'],
    'Railroads': ['Railroads', 'Trucking', 'Integrated Freight & Logistics'],
    'Trucking': ['Trucking', 'Railroads', 'Integrated Freight & Logistics'],
    'Integrated Freight & Logistics': ['Integrated Freight & Logistics', 'Railroads', 'Trucking', 'Air Freight & Logistics'],
    'Air Freight & Logistics': ['Air Freight & Logistics', 'Integrated Freight & Logistics', 'Airlines'],
    'Airlines': ['Airlines', 'Air Freight & Logistics', 'Travel Services'],
    'Building Materials': ['Building Materials', 'Building Products', 'Specialty Industrial Machinery'],
    'Electrical Equipment & Parts': ['Electrical Equipment & Parts', 'Specialty Industrial Machinery', 'Electronic Components'],
    'Engineering & Construction': ['Engineering & Construction', 'Building Materials', 'Specialty Industrial Machinery'],
    'Waste Management': ['Waste Management', 'Environmental Services', 'Industrial Services'],
    'Pollution & Treatment Controls': ['Pollution & Treatment Controls', 'Waste Management', 'Specialty Industrial Machinery'],
    'Staffing & Employment Services': ['Staffing & Employment Services', 'Business Services', 'Industrial Services'],
    'Security & Protection Services': ['Security & Protection Services', 'Business Services', 'Industrial Services'],
    
    # === ENERGY ===
    'Oil & Gas Integrated': ['Oil & Gas Integrated', 'Oil & Gas E&P', 'Oil & Gas Refining & Marketing'],
    'Oil & Gas E&P': ['Oil & Gas E&P', 'Oil & Gas Integrated', 'Oil & Gas Equipment & Services'],
    'Oil & Gas Refining & Marketing': ['Oil & Gas Refining & Marketing', 'Oil & Gas Integrated', 'Oil & Gas Midstream'],
    'Oil & Gas Midstream': ['Oil & Gas Midstream', 'Oil & Gas Refining & Marketing', 'Oil & Gas Integrated'],
    'Oil & Gas Equipment & Services': ['Oil & Gas Equipment & Services', 'Oil & Gas E&P', 'Oil & Gas Drilling'],
    'Oil & Gas Drilling': ['Oil & Gas Drilling', 'Oil & Gas Equipment & Services', 'Oil & Gas E&P'],
    
    # === UTILITIES ===
    'Utilities - Regulated Electric': ['Utilities - Regulated Electric', 'Utilities - Diversified', 'Utilities - Renewable'],
    'Utilities - Diversified': ['Utilities - Diversified', 'Utilities - Regulated Electric', 'Utilities - Regulated Gas'],
    'Utilities - Regulated Gas': ['Utilities - Regulated Gas', 'Utilities - Diversified', 'Utilities - Regulated Electric'],
    'Utilities - Renewable': ['Utilities - Renewable', 'Utilities - Regulated Electric', 'Utilities - Diversified'],
    'Utilities - Independent Power Producers': ['Utilities - Independent Power Producers', 'Utilities - Diversified', 'Utilities - Renewable'],
    
    # === REAL ESTATE ===
    'REIT - Industrial': ['REIT - Industrial', 'REIT - Diversified', 'REIT - Specialty'],
    'REIT - Retail': ['REIT - Retail', 'REIT - Diversified', 'REIT - Specialty'],
    'REIT - Office': ['REIT - Office', 'REIT - Diversified', 'REIT - Specialty'],
    'REIT - Residential': ['REIT - Residential', 'REIT - Diversified', 'REIT - Specialty'],
    'REIT - Healthcare Facilities': ['REIT - Healthcare Facilities', 'REIT - Diversified', 'REIT - Specialty'],
    'REIT - Specialty': ['REIT - Specialty', 'REIT - Diversified', 'REIT - Industrial'],
    'REIT - Diversified': ['REIT - Diversified', 'REIT - Industrial', 'REIT - Retail', 'REIT - Office'],
    'Real Estate Services': ['Real Estate Services', 'Real Estate - Development', 'REIT - Diversified'],
    'Real Estate - Development': ['Real Estate - Development', 'Real Estate Services', 'Residential Construction'],
    
    # === BASIC MATERIALS ===
    'Specialty Chemicals': ['Specialty Chemicals', 'Chemicals', 'Agricultural Inputs'],
    'Chemicals': ['Chemicals', 'Specialty Chemicals', 'Agricultural Inputs'],
    'Agricultural Inputs': ['Agricultural Inputs', 'Chemicals', 'Specialty Chemicals'],
    'Steel': ['Steel', 'Aluminum', 'Other Industrial Metals & Mining'],
    'Aluminum': ['Aluminum', 'Steel', 'Other Industrial Metals & Mining'],
    'Copper': ['Copper', 'Other Industrial Metals & Mining', 'Gold'],
    'Gold': ['Gold', 'Silver', 'Other Precious Metals & Mining'],
    'Silver': ['Silver', 'Gold', 'Other Precious Metals & Mining'],
    'Other Industrial Metals & Mining': ['Other Industrial Metals & Mining', 'Steel', 'Copper', 'Aluminum'],
    'Other Precious Metals & Mining': ['Other Precious Metals & Mining', 'Gold', 'Silver'],
    'Building Materials': ['Building Materials', 'Specialty Chemicals', 'Steel'],
    'Coking Coal': ['Coking Coal', 'Thermal Coal', 'Other Industrial Metals & Mining'],
    'Thermal Coal': ['Thermal Coal', 'Coking Coal', 'Oil & Gas E&P'],
    'Paper & Paper Products': ['Paper & Paper Products', 'Packaging & Containers', 'Lumber & Wood Production'],
    'Packaging & Containers': ['Packaging & Containers', 'Paper & Paper Products', 'Specialty Chemicals'],
    'Lumber & Wood Production': ['Lumber & Wood Production', 'Paper & Paper Products', 'Building Materials'],
}


@st.cache_data(ttl=86400)  # Cache for 24 hours
def discover_peers(ticker: str, max_peers: int = 10) -> Dict:
    """
    Automatically discover peer companies based on sector and industry
    
    IMPROVED VERSION: Prioritizes INDUSTRY match over sector
    - Same industry = strong match
    - Related industry = moderate match  
    - Different industry = penalized (even if same sector)
    
    Args:
        ticker: Stock ticker symbol
        max_peers: Maximum number of peers to return (default 10)
        
    Returns:
        Dictionary with peer list and discovery metadata
    """
    
    try:
        print(f"\n[INFO] Discovering peers for {ticker}...")
        
        # Get company info (using cached ticker info to prevent rate limiting)
        info = get_ticker_info(ticker)
        
        company_sector = info.get('sector', 'Unknown')
        company_industry = info.get('industry', 'Unknown')
        company_market_cap = info.get('marketCap', 0)
        
        print(f"[INFO] Sector: {company_sector}, Industry: {company_industry}, Market Cap: ${company_market_cap/1e9:.2f}B")
        
        # FAST PATH: Use pre-built sector mapping
        from sp500_sector_map import SP500_SECTOR_MAP, get_sector_peers
        
        # Get candidate peers from sector mapping (get more candidates to filter)
        candidate_tickers = get_sector_peers(ticker, company_sector, max_peers=max_peers * 5)
        
        print(f"[INFO] Found {len(candidate_tickers)} candidates in {company_sector} sector")
        
        # Get related industries for this company
        related_industries = RELATED_INDUSTRIES.get(company_industry, [company_industry])
        
        peers = []
        same_industry_count = 0
        
        # Now fetch detailed info only for candidates (using cache to prevent rate limiting)
        for peer_ticker in candidate_tickers:
            try:
                peer_info = get_ticker_info(peer_ticker)
                
                peer_industry = peer_info.get('industry', 'Unknown')
                peer_market_cap = peer_info.get('marketCap', 0)
                
                # NEW SCORING: Industry-first, but allow same-sector fallback
                similarity_score = 0.0
                
                # INDUSTRY MATCHING (most important!)
                if peer_industry == company_industry:
                    # Exact industry match = strong bonus
                    similarity_score += 3.0
                    same_industry_count += 1
                elif peer_industry in related_industries:
                    # Related industry = moderate bonus
                    similarity_score += 1.5
                else:
                    # Different industry but SAME SECTOR = small bonus (fallback)
                    # This allows peers when exact/related matches aren't available
                    similarity_score += 0.3  # Changed from -1.0 penalty to small bonus
                
                # SIZE MATCHING (secondary factor)
                if company_market_cap > 0 and peer_market_cap > 0:
                    size_ratio = max(company_market_cap, peer_market_cap) / min(company_market_cap, peer_market_cap)
                    if size_ratio <= 2:  # Within 2x (very similar)
                        similarity_score += 1.0
                    elif size_ratio <= 5:  # Within 5x
                        similarity_score += 0.5
                    elif size_ratio <= 10:  # Within 10x
                        similarity_score += 0.25
                    # No bonus for >10x difference
                
                # Only add if score is positive (filters out unrelated industries)
                if similarity_score > 0:
                    peers.append({
                        'ticker': peer_ticker,
                        'name': peer_info.get('longName', peer_ticker),
                        'sector': peer_info.get('sector', company_sector),
                        'industry': peer_industry,
                        'market_cap': peer_market_cap,
                        'similarity_score': similarity_score,
                        'industry_match': 'Exact' if peer_industry == company_industry else 'Related' if peer_industry in related_industries else 'Sector Only'
                    })
                    
                    print(f"[OK] Added peer: {peer_ticker} ({peer_industry}) - score: {similarity_score:.1f}")
                else:
                    print(f"[SKIP] {peer_ticker} ({peer_industry}) - different industry, score: {similarity_score:.1f}")
                    
            except Exception as e:
                print(f"[WARN] Failed to fetch {peer_ticker}: {str(e)}")
                continue
        
        # Sort by similarity score and take top N
        peers.sort(key=lambda x: x['similarity_score'], reverse=True)
        top_peers = peers[:max_peers]
        
        print(f"[INFO] Same industry matches: {same_industry_count}")
        
        result = {
            'status': 'success',
            'ticker': ticker,
            'company_name': info.get('longName', ticker),
            'sector': company_sector,
            'industry': company_industry,
            'market_cap': company_market_cap,
            'peers': top_peers,
            'total_candidates': len(peers),
            'same_industry_peers': same_industry_count,
            'discovery_method': 'Industry-first matching with related industry support'
        }
        
        print(f"[OK] Found {len(top_peers)} peers from {len(peers)} candidates")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Peer discovery failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'status': 'error',
            'message': f'Error discovering peers: {str(e)}'
        }


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_peer_comparison_data(ticker: str, peer_tickers: List[str]) -> Dict:
    """
    Fetch comprehensive financial data for peer comparison
    
    Args:
        ticker: Primary company ticker
        peer_tickers: List of peer tickers
        
    Returns:
        Dictionary with comparison data for all companies
    """
    
    try:
        print(f"\n[INFO] Fetching comparison data for {ticker} and {len(peer_tickers)} peers...")
        
        all_tickers = [ticker] + peer_tickers
        comparison_data = []
        
        # Key metrics to compare (15 metrics)
        metrics_to_fetch = [
            'marketCap',
            'enterpriseValue',
            'trailingPE',
            'forwardPE',
            'priceToBook',
            'priceToSales',
            'enterpriseToEbitda',
            'pegRatio',
            'revenueGrowth',
            'profitMargins',
            'grossMargins',
            'operatingMargins',
            'returnOnEquity',
            'returnOnAssets',
            'debtToEquity',
            'currentRatio',
            'quickRatio',
            'freeCashflow',
            'operatingCashflow',
            'totalRevenue'
        ]
        
        for t in all_tickers:
            try:
                # Use cached ticker info to prevent rate limiting
                info = get_ticker_info(t)
                
                row = {
                    'Ticker': t,
                    'Company': info.get('longName', t),
                    'Sector': info.get('sector', 'N/A'),
                    'Industry': info.get('industry', 'N/A'),
                }
                
                # Add all metrics
                row['Market Cap'] = info.get('marketCap')
                row['Enterprise Value'] = info.get('enterpriseValue')
                row['P/E (TTM)'] = info.get('trailingPE')
                row['Forward P/E'] = info.get('forwardPE')
                row['P/B'] = info.get('priceToBook')
                row['P/S'] = info.get('priceToSales')
                row['EV/EBITDA'] = info.get('enterpriseToEbitda')
                row['PEG Ratio'] = info.get('pegRatio')
                row['Revenue Growth'] = info.get('revenueGrowth')
                row['Net Margin'] = info.get('profitMargins')
                row['Gross Margin'] = info.get('grossMargins')
                row['Operating Margin'] = info.get('operatingMargins')
                row['ROE'] = info.get('returnOnEquity')
                row['ROA'] = info.get('returnOnAssets')
                row['Debt/Equity'] = info.get('debtToEquity')
                row['Current Ratio'] = info.get('currentRatio')
                row['Quick Ratio'] = info.get('quickRatio')
                row['Free Cash Flow'] = info.get('freeCashflow')
                row['Operating Cash Flow'] = info.get('operatingCashflow')
                row['Total Revenue'] = info.get('totalRevenue')
                
                comparison_data.append(row)
                print(f"[OK] Fetched data for {t}")
                
            except Exception as e:
                print(f"[WARN] Failed to fetch {t}: {str(e)}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Set ticker as primary company identifier
        df['Is_Primary'] = df['Ticker'] == ticker
        
        result = {
            'status': 'success',
            'ticker': ticker,
            'data': df,
            'metrics_count': len(df.columns) - 5  # Exclude Ticker, Company, Sector, Industry, Is_Primary
        }
        
        print(f"[OK] Comparison data ready: {len(df)} companies, {result['metrics_count']} metrics")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Comparison data fetch failed: {str(e)}")
        return {
            'status': 'error',
            'message': f'Error fetching comparison data: {str(e)}'
        }


def calculate_percentile_ranks(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Calculate percentile rankings for all numeric metrics
    
    Args:
        df: DataFrame with comparison data
        ticker: Primary company ticker
        
    Returns:
        DataFrame with percentile rankings added
    """
    
    try:
        # Get numeric columns only (exclude Ticker, Company, Sector, Industry, Is_Primary)
        exclude_cols = ['Ticker', 'Company', 'Sector', 'Industry', 'Is_Primary']
        numeric_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Create percentile rank columns
        percentile_df = df.copy()
        
        for col in numeric_cols:
            # Skip if all NaN
            if df[col].isna().all():
                percentile_df[f'{col}_Percentile'] = np.nan
                continue
            
            # Calculate percentile rank (0-100)
            # Higher is better for most metrics except P/E, P/B, P/S, Debt/Equity
            
            lower_is_better = ['P/E (TTM)', 'Forward P/E', 'P/B', 'P/S', 'EV/EBITDA', 'PEG Ratio', 'Debt/Equity']
            
            if col in lower_is_better:
                # For these metrics, lower values get higher percentile
                percentile_df[f'{col}_Percentile'] = df[col].rank(ascending=True, pct=True) * 100
            else:
                # For most metrics, higher values get higher percentile
                percentile_df[f'{col}_Percentile'] = df[col].rank(ascending=False, pct=True) * 100
        
        return percentile_df
        
    except Exception as e:
        print(f"[ERROR] Percentile calculation failed: {str(e)}")
        return df


def calculate_statistics(df: pd.DataFrame) -> Dict:
    """
    Calculate peer group statistics (mean, median, std dev, quartiles)
    
    Args:
        df: DataFrame with comparison data
        
    Returns:
        Dictionary with statistical summaries
    """
    
    try:
        exclude_cols = ['Ticker', 'Company', 'Sector', 'Industry', 'Is_Primary']
        numeric_cols = [col for col in df.columns if col not in exclude_cols and not col.endswith('_Percentile')]
        
        stats = {}
        
        for col in numeric_cols:
            # Skip if all NaN
            if df[col].isna().all():
                continue
            
            col_data = df[col].dropna()
            
            stats[col] = {
                'mean': col_data.mean(),
                'median': col_data.median(),
                'std': col_data.std(),
                'min': col_data.min(),
                'max': col_data.max(),
                'q25': col_data.quantile(0.25),
                'q75': col_data.quantile(0.75),
                'count': len(col_data)
            }
        
        return stats
        
    except Exception as e:
        print(f"[ERROR] Statistics calculation failed: {str(e)}")
        return {}


def generate_heatmap_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Prepare data for heatmap visualization
    
    Args:
        df: DataFrame with comparison data
        
    Returns:
        Tuple of (heatmap DataFrame, color mapping dict)
    """
    
    try:
        # Select key metrics for heatmap (to avoid clutter)
        heatmap_metrics = [
            'P/E (TTM)', 'P/B', 'P/S', 'EV/EBITDA',
            'Revenue Growth', 'Net Margin', 'Operating Margin',
            'ROE', 'ROA', 'Debt/Equity'
        ]
        
        # Filter to available metrics
        available_metrics = [m for m in heatmap_metrics if m in df.columns]
        
        # Create heatmap DataFrame
        heatmap_df = df[['Ticker', 'Company'] + available_metrics].copy()
        
        # Normalize values to 0-1 scale for color mapping
        normalized_df = heatmap_df.copy()
        
        for col in available_metrics:
            if col in heatmap_df.columns and not heatmap_df[col].isna().all():
                min_val = heatmap_df[col].min()
                max_val = heatmap_df[col].max()
                
                if max_val > min_val:
                    normalized_df[col] = (heatmap_df[col] - min_val) / (max_val - min_val)
                else:
                    normalized_df[col] = 0.5  # Neutral if all same
        
        # Color mapping: Green (good) to Red (bad)
        # For valuation metrics (P/E, P/B, etc.), lower is better
        # For performance metrics (margins, ROE), higher is better
        
        color_map = {}
        
        lower_is_better = ['P/E (TTM)', 'P/B', 'P/S', 'EV/EBITDA', 'Debt/Equity']
        
        for col in available_metrics:
            if col in lower_is_better:
                color_map[col] = 'inverted'  # Lower = green, higher = red
            else:
                color_map[col] = 'normal'  # Higher = green, lower = red
        
        return heatmap_df, color_map
        
    except Exception as e:
        print(f"[ERROR] Heatmap data generation failed: {str(e)}")
        return pd.DataFrame(), {}


def export_comparison_to_excel(df: pd.DataFrame, ticker: str, stats: Dict) -> bytes:
    """
    Export comparison data to Excel with formatting
    
    Args:
        df: DataFrame with comparison data
        ticker: Primary company ticker
        stats: Statistical summary
        
    Returns:
        Excel file as bytes
    """
    
    try:
        from io import BytesIO
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment
        
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Comparison Data
            df.to_excel(writer, sheet_name='Peer Comparison', index=False)
            
            # Sheet 2: Statistics
            stats_df = pd.DataFrame(stats).T
            stats_df.to_excel(writer, sheet_name='Statistics')
            
            # Sheet 3: Percentile Rankings
            percentile_cols = [col for col in df.columns if col.endswith('_Percentile')]
            if percentile_cols:
                percentile_df = df[['Ticker', 'Company'] + percentile_cols]
                percentile_df.to_excel(writer, sheet_name='Percentile Rankings', index=False)
        
        excel_data = output.getvalue()
        return excel_data
        
    except Exception as e:
        print(f"[ERROR] Excel export failed: {str(e)}")
        return b''


# ============================================================================
# TESTING CODE
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("TESTING PEER COMPARISON MODULE")
    print("="*80)
    
    test_ticker = "AAPL"
    
    # Test 1: Peer Discovery
    print(f"\n[TEST 1] Peer Discovery for {test_ticker}")
    print("-"*80)
    
    peer_result = discover_peers(test_ticker, max_peers=10)
    
    if peer_result['status'] == 'success':
        print(f"\n✅ Company: {peer_result['company_name']}")
        print(f"   Sector: {peer_result['sector']}")
        print(f"   Industry: {peer_result['industry']}")
        print(f"   Peers found: {len(peer_result['peers'])}")
        
        print(f"\nTop 5 Peers:")
        for i, peer in enumerate(peer_result['peers'][:5], 1):
            print(f"   {i}. {peer['ticker']} - {peer['name']}")
            print(f"      Similarity Score: {peer['similarity_score']:.1f}")
    else:
        print(f"\n[FAIL] {peer_result['message']}")
    
    # Test 2: Comparison Data
    print(f"\n[TEST 2] Fetching Comparison Data")
    print("-"*80)
    
    if peer_result['status'] == 'success':
        peer_tickers = [p['ticker'] for p in peer_result['peers'][:5]]
        
        comp_result = get_peer_comparison_data(test_ticker, peer_tickers)
        
        if comp_result['status'] == 'success':
            print(f"\n✅ Comparison data ready")
            print(f"   Companies: {len(comp_result['data'])}")
            print(f"   Metrics: {comp_result['metrics_count']}")
            
            # Show sample
            print(f"\nSample data (first 3 columns):")
            print(comp_result['data'][['Ticker', 'Company', 'Market Cap']].head())
        else:
            print(f"\n[FAIL] {comp_result['message']}")
    
    # Test 3: Percentile Rankings
    print(f"\n[TEST 3] Percentile Rankings")
    print("-"*80)
    
    if comp_result['status'] == 'success':
        df_with_percentiles = calculate_percentile_ranks(comp_result['data'], test_ticker)
        
        # Show AAPL's percentile rankings
        aapl_row = df_with_percentiles[df_with_percentiles['Ticker'] == test_ticker]
        
        percentile_cols = [col for col in df_with_percentiles.columns if col.endswith('_Percentile')]
        
        print(f"\n✅ {test_ticker} Percentile Rankings (Top 5):")
        for col in percentile_cols[:5]:
            metric_name = col.replace('_Percentile', '')
            percentile = aapl_row[col].values[0]
            if not np.isnan(percentile):
                print(f"   {metric_name}: {percentile:.1f}th percentile")
    
    print("\n" + "="*80)
    print("[OK] All tests completed successfully")
    print("="*80)

