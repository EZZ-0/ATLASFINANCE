"""
GICS to Damodaran Sector Mapping
=================================
Maps GICS (Global Industry Classification Standard) sectors and industries
to Aswath Damodaran's industry classifications.

This mapping is essential for:
- Looking up industry benchmarks (betas, WACC, multiples)
- Comparing company metrics to industry averages
- Sector-based validation

GICS Structure:
- 11 Sectors → 24 Industry Groups → 69 Industries → 158 Sub-Industries

Damodaran has ~100 industries on his datasets.

Author: ATLAS Financial Intelligence
Created: 2025-12-07 (TASK-E006)
"""

from typing import Optional, Dict, List, Tuple

# ==========================================
# GICS SECTOR MAPPINGS
# ==========================================

# Map GICS Sector → Damodaran Industry (broad match)
GICS_SECTOR_TO_DAMODARAN = {
    # Technology (45)
    'Information Technology': 'Computers/Peripherals',
    'Technology': 'Computers/Peripherals',
    
    # Healthcare (35)
    'Health Care': 'Healthcare Products',
    'Healthcare': 'Healthcare Products',
    
    # Financials (40)
    'Financials': 'Financial Svcs. (Non-bank & Insurance)',
    
    # Consumer Discretionary (25)
    'Consumer Discretionary': 'Retail (General)',
    
    # Consumer Staples (30)
    'Consumer Staples': 'Food Processing',
    
    # Industrials (20)
    'Industrials': 'Diversified',
    
    # Energy (10)
    'Energy': 'Oil/Gas (Integrated)',
    
    # Materials (15)
    'Materials': 'Chemical (Basic)',
    
    # Real Estate (60)
    'Real Estate': 'REIT',
    
    # Utilities (55)
    'Utilities': 'Utility (General)',
    
    # Communication Services (50)
    'Communication Services': 'Telecom. Services',
    'Communication': 'Telecom. Services',
}


# ==========================================
# GICS INDUSTRY GROUP MAPPINGS (24 groups)
# ==========================================

GICS_INDUSTRY_GROUP_TO_DAMODARAN = {
    # Technology
    'Software & Services': 'Software (System & Application)',
    'Technology Hardware & Equipment': 'Computers/Peripherals',
    'Semiconductors & Semiconductor Equipment': 'Semiconductor',
    
    # Healthcare
    'Pharmaceuticals, Biotechnology & Life Sciences': 'Drugs (Pharmaceutical)',
    'Health Care Equipment & Services': 'Healthcare Products',
    
    # Financials
    'Banks': 'Banks (Regional)',
    'Diversified Financials': 'Financial Svcs. (Non-bank & Insurance)',
    'Insurance': 'Insurance (General)',
    
    # Consumer Discretionary
    'Consumer Services': 'Hotel/Gaming',
    'Consumer Durables & Apparel': 'Apparel',
    'Retailing': 'Retail (General)',
    'Automobiles & Components': 'Auto Parts',
    
    # Consumer Staples
    'Food, Beverage & Tobacco': 'Food Processing',
    'Food & Staples Retailing': 'Retail (Grocery and Food)',
    'Household & Personal Products': 'Household Products',
    
    # Industrials
    'Capital Goods': 'Machinery',
    'Commercial & Professional Services': 'Business & Consumer Services',
    'Transportation': 'Transportation',
    
    # Energy
    'Energy': 'Oil/Gas (Integrated)',
    
    # Materials
    'Materials': 'Chemical (Basic)',
    
    # Real Estate
    'Real Estate': 'REIT',
    'Equity Real Estate Investment Trusts (REITs)': 'REIT',
    'Real Estate Management & Development': 'Real Estate (Development)',
    
    # Utilities
    'Utilities': 'Utility (General)',
    
    # Communication
    'Telecommunication Services': 'Telecom. Services',
    'Media & Entertainment': 'Entertainment',
}


# ==========================================
# GICS INDUSTRY MAPPINGS (69 industries)
# ==========================================

GICS_INDUSTRY_TO_DAMODARAN = {
    # TECHNOLOGY
    'Software': 'Software (System & Application)',
    'IT Services': 'Information Services',
    'Communications Equipment': 'Telecom. Equipment',
    'Technology Hardware, Storage & Peripherals': 'Computers/Peripherals',
    'Electronic Equipment, Instruments & Components': 'Electronics (Consumer & Office)',
    'Semiconductors & Semiconductor Equipment': 'Semiconductor',
    
    # HEALTHCARE
    'Pharmaceuticals': 'Drugs (Pharmaceutical)',
    'Biotechnology': 'Drugs (Biotechnology)',
    'Life Sciences Tools & Services': 'Healthcare Products',
    'Health Care Equipment & Supplies': 'Healthcare Products',
    'Health Care Providers & Services': 'Healthcare Support Services',
    'Health Care Technology': 'Healthcare Information and Technology',
    
    # FINANCIALS
    'Diversified Banks': 'Banks (Money Center)',
    'Regional Banks': 'Banks (Regional)',
    'Thrifts & Mortgage Finance': 'Financial Svcs. (Non-bank & Insurance)',
    'Consumer Finance': 'Financial Svcs. (Non-bank & Insurance)',
    'Capital Markets': 'Investment Co.',
    'Mortgage Real Estate Investment Trusts (REITs)': 'REIT',
    'Insurance': 'Insurance (General)',
    'Multi-line Insurance': 'Insurance (General)',
    'Property & Casualty Insurance': 'Insurance (Prop/Cas.)',
    'Life & Health Insurance': 'Insurance (Life)',
    'Reinsurance': 'Insurance (General)',
    
    # CONSUMER DISCRETIONARY
    'Auto Components': 'Auto Parts',
    'Automobiles': 'Auto & Truck',
    'Household Durables': 'Household Products',
    'Leisure Products': 'Recreation',
    'Textiles, Apparel & Luxury Goods': 'Apparel',
    'Hotels, Restaurants & Leisure': 'Hotel/Gaming',
    'Diversified Consumer Services': 'Business & Consumer Services',
    'Distributors': 'Retail (Distributors)',
    'Internet & Direct Marketing Retail': 'Retail (Online)',
    'Multiline Retail': 'Retail (General)',
    'Specialty Retail': 'Retail (Special Lines)',
    
    # CONSUMER STAPLES
    'Food & Staples Retailing': 'Retail (Grocery and Food)',
    'Beverages': 'Beverage (Soft)',
    'Food Products': 'Food Processing',
    'Tobacco': 'Tobacco',
    'Household Products': 'Household Products',
    'Personal Products': 'Household Products',
    
    # INDUSTRIALS
    'Aerospace & Defense': 'Aerospace/Defense',
    'Building Products': 'Building Materials',
    'Construction & Engineering': 'Engineering/Construction',
    'Electrical Equipment': 'Electrical Equipment',
    'Industrial Conglomerates': 'Diversified',
    'Machinery': 'Machinery',
    'Trading Companies & Distributors': 'Retail (Distributors)',
    'Commercial Services & Supplies': 'Business & Consumer Services',
    'Professional Services': 'Business & Consumer Services',
    'Air Freight & Logistics': 'Air Transport',
    'Airlines': 'Air Transport',
    'Marine': 'Shipbuilding & Marine',
    'Road & Rail': 'Transportation (Railroads)',
    'Transportation Infrastructure': 'Transportation',
    
    # ENERGY
    'Energy Equipment & Services': 'Oilfield Svcs/Equip.',
    'Oil, Gas & Consumable Fuels': 'Oil/Gas (Integrated)',
    'Oil & Gas': 'Oil/Gas (Integrated)',
    
    # MATERIALS
    'Chemicals': 'Chemical (Basic)',
    'Construction Materials': 'Building Materials',
    'Containers & Packaging': 'Packaging & Container',
    'Metals & Mining': 'Metals & Mining',
    'Paper & Forest Products': 'Paper/Forest Products',
    
    # REAL ESTATE
    'Equity Real Estate Investment Trusts (REITs)': 'REIT',
    'Real Estate Management & Development': 'Real Estate (Development)',
    
    # UTILITIES
    'Electric Utilities': 'Utility (General)',
    'Gas Utilities': 'Utility (General)',
    'Multi-Utilities': 'Utility (General)',
    'Water Utilities': 'Utility (Water)',
    'Independent Power and Renewable Electricity Producers': 'Power',
    
    # COMMUNICATION
    'Diversified Telecommunication Services': 'Telecom. Services',
    'Wireless Telecommunication Services': 'Telecom. (Wireless)',
    'Media': 'Broadcasting',
    'Entertainment': 'Entertainment',
    'Interactive Media & Services': 'Entertainment Tech',
}


# ==========================================
# COMMON TICKER → SECTOR OVERRIDES
# ==========================================

# For specific tickers where general mapping might be wrong
TICKER_SECTOR_OVERRIDES = {
    'AAPL': ('Technology Hardware, Storage & Peripherals', 'Computers/Peripherals'),
    'MSFT': ('Software', 'Software (System & Application)'),
    'GOOGL': ('Interactive Media & Services', 'Entertainment Tech'),
    'GOOG': ('Interactive Media & Services', 'Entertainment Tech'),
    'AMZN': ('Internet & Direct Marketing Retail', 'Retail (Online)'),
    'META': ('Interactive Media & Services', 'Entertainment Tech'),
    'NVDA': ('Semiconductors & Semiconductor Equipment', 'Semiconductor'),
    'TSLA': ('Automobiles', 'Auto & Truck'),
    'JPM': ('Diversified Banks', 'Banks (Money Center)'),
    'JNJ': ('Pharmaceuticals', 'Drugs (Pharmaceutical)'),
    'V': ('IT Services', 'Information Services'),
    'MA': ('IT Services', 'Information Services'),
    'UNH': ('Health Care Providers & Services', 'Healthcare Support Services'),
    'PG': ('Household Products', 'Household Products'),
    'HD': ('Specialty Retail', 'Retail (Building Supply)'),
    'CVX': ('Oil, Gas & Consumable Fuels', 'Oil/Gas (Integrated)'),
    'XOM': ('Oil, Gas & Consumable Fuels', 'Oil/Gas (Integrated)'),
    'PFE': ('Pharmaceuticals', 'Drugs (Pharmaceutical)'),
    'ABBV': ('Biotechnology', 'Drugs (Biotechnology)'),
    'KO': ('Beverages', 'Beverage (Soft)'),
    'PEP': ('Beverages', 'Beverage (Soft)'),
    'MRK': ('Pharmaceuticals', 'Drugs (Pharmaceutical)'),
    'WMT': ('Food & Staples Retailing', 'Retail (Grocery and Food)'),
    'DIS': ('Entertainment', 'Entertainment'),
    'NFLX': ('Entertainment', 'Entertainment'),
    'CRM': ('Software', 'Software (System & Application)'),
    'ADBE': ('Software', 'Software (System & Application)'),
    'INTC': ('Semiconductors & Semiconductor Equipment', 'Semiconductor'),
    'AMD': ('Semiconductors & Semiconductor Equipment', 'Semiconductor'),
    'BA': ('Aerospace & Defense', 'Aerospace/Defense'),
    'CAT': ('Machinery', 'Machinery'),
    'GE': ('Industrial Conglomerates', 'Diversified'),
    'MMM': ('Industrial Conglomerates', 'Diversified'),
}


# ==========================================
# LOOKUP FUNCTIONS
# ==========================================

def get_damodaran_industry(
    gics_sector: Optional[str] = None,
    gics_industry_group: Optional[str] = None,
    gics_industry: Optional[str] = None,
    ticker: Optional[str] = None
) -> Tuple[str, str]:
    """
    Get Damodaran industry name from GICS classification.
    
    Args:
        gics_sector: GICS Sector (e.g., "Technology")
        gics_industry_group: GICS Industry Group (e.g., "Software & Services")
        gics_industry: GICS Industry (e.g., "Software")
        ticker: Optional ticker for override lookup
        
    Returns:
        Tuple of (damodaran_industry, match_type)
        match_type: 'ticker_override', 'industry', 'industry_group', 'sector', 'default'
    """
    # 1. Check ticker override first
    if ticker and ticker.upper() in TICKER_SECTOR_OVERRIDES:
        _, damodaran = TICKER_SECTOR_OVERRIDES[ticker.upper()]
        return damodaran, 'ticker_override'
    
    # 2. Try industry (most specific)
    if gics_industry:
        clean = gics_industry.strip()
        if clean in GICS_INDUSTRY_TO_DAMODARAN:
            return GICS_INDUSTRY_TO_DAMODARAN[clean], 'industry'
    
    # 3. Try industry group
    if gics_industry_group:
        clean = gics_industry_group.strip()
        if clean in GICS_INDUSTRY_GROUP_TO_DAMODARAN:
            return GICS_INDUSTRY_GROUP_TO_DAMODARAN[clean], 'industry_group'
    
    # 4. Try sector
    if gics_sector:
        clean = gics_sector.strip()
        if clean in GICS_SECTOR_TO_DAMODARAN:
            return GICS_SECTOR_TO_DAMODARAN[clean], 'sector'
    
    # 5. Default
    return 'Total Market', 'default'


def get_sector_for_ticker(ticker: str, yfinance_info: Optional[Dict] = None) -> Dict:
    """
    Get full sector mapping for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        yfinance_info: Optional yfinance info dict (to extract GICS classification)
        
    Returns:
        {
            'ticker': 'AAPL',
            'gics_sector': 'Information Technology',
            'gics_industry': 'Technology Hardware, Storage & Peripherals',
            'damodaran_industry': 'Computers/Peripherals',
            'match_type': 'ticker_override',
            'is_override': True
        }
    """
    result = {
        'ticker': ticker.upper(),
        'gics_sector': None,
        'gics_industry_group': None,
        'gics_industry': None,
        'damodaran_industry': None,
        'match_type': None,
        'is_override': False
    }
    
    # Extract from yfinance info if provided
    if yfinance_info:
        result['gics_sector'] = yfinance_info.get('sector')
        result['gics_industry'] = yfinance_info.get('industry')
    
    # Check for override
    if ticker.upper() in TICKER_SECTOR_OVERRIDES:
        gics, damodaran = TICKER_SECTOR_OVERRIDES[ticker.upper()]
        result['gics_industry'] = gics
        result['damodaran_industry'] = damodaran
        result['match_type'] = 'ticker_override'
        result['is_override'] = True
    else:
        # Use lookup
        damodaran, match_type = get_damodaran_industry(
            gics_sector=result['gics_sector'],
            gics_industry=result['gics_industry'],
            ticker=ticker
        )
        result['damodaran_industry'] = damodaran
        result['match_type'] = match_type
    
    return result


def list_all_damodaran_industries() -> List[str]:
    """Get list of all Damodaran industry names used in mappings."""
    industries = set()
    
    industries.update(GICS_SECTOR_TO_DAMODARAN.values())
    industries.update(GICS_INDUSTRY_GROUP_TO_DAMODARAN.values())
    industries.update(GICS_INDUSTRY_TO_DAMODARAN.values())
    industries.update(dam for _, dam in TICKER_SECTOR_OVERRIDES.values())
    
    return sorted(industries)


def get_coverage_stats() -> Dict:
    """Get mapping coverage statistics."""
    return {
        'sectors_mapped': len(GICS_SECTOR_TO_DAMODARAN),
        'industry_groups_mapped': len(GICS_INDUSTRY_GROUP_TO_DAMODARAN),
        'industries_mapped': len(GICS_INDUSTRY_TO_DAMODARAN),
        'ticker_overrides': len(TICKER_SECTOR_OVERRIDES),
        'unique_damodaran_industries': len(list_all_damodaran_industries())
    }


# ==========================================
# TEST / EXAMPLE
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("GICS TO DAMODARAN SECTOR MAPPING TEST")
    print("=" * 60)
    
    # Coverage stats
    stats = get_coverage_stats()
    print(f"\nMapping Coverage:")
    print(f"  GICS Sectors: {stats['sectors_mapped']}")
    print(f"  Industry Groups: {stats['industry_groups_mapped']}")
    print(f"  Industries: {stats['industries_mapped']}")
    print(f"  Ticker Overrides: {stats['ticker_overrides']}")
    print(f"  Unique Damodaran Industries: {stats['unique_damodaran_industries']}")
    
    # Test specific tickers
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'JPM', 'JNJ', 'XOM', 'UNKNOWN']
    
    print(f"\nTicker Lookups:")
    for ticker in test_tickers:
        result = get_sector_for_ticker(ticker)
        print(f"  {ticker}: {result['damodaran_industry']} ({result['match_type']})")
    
    # Test industry lookup
    print(f"\nIndustry Lookups:")
    test_industries = ['Software', 'Pharmaceuticals', 'Diversified Banks']
    for industry in test_industries:
        damodaran, match_type = get_damodaran_industry(gics_industry=industry)
        print(f"  {industry} → {damodaran}")
    
    print("\n[OK] Mapping module ready")

