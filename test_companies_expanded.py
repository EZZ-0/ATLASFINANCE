"""
EXPANDED TEST COMPANY SET
=========================
50 companies across 11 sectors, stratified by market cap and profitability

Coverage:
- 11 sectors (proportional to S&P 500)
- Large/Mid/Small cap mix
- Profitable + Loss-making companies
- High/Low leverage companies
- Special situations (turnarounds, IPOs, etc.)
"""

# ==========================================
# EXPANDED TEST SET: 50 COMPANIES
# ==========================================

EXPANDED_TEST_SET = {
    # ===================================
    # TECHNOLOGY (10 companies)
    # ===================================
    'Technology': {
        'large_cap': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA'],  # Mega-cap tech
        'mid_cap': ['CRM', 'ADBE', 'ORCL'],  # Enterprise software
        'growth': ['SNOW', 'DDOG'],  # High-growth SaaS
        'turnaround': []
    },
    
    # ===================================
    # FINANCIALS (8 companies)
    # ===================================
    'Financials': {
        'banks': ['JPM', 'BAC', 'C', 'WFC'],  # Major banks
        'insurance': ['BRK-B', 'PGR'],  # Insurance/diversified
        'asset_mgmt': ['BLK', 'SCHW'],  # Asset managers
        'fintech': []
    },
    
    # ===================================
    # HEALTHCARE (7 companies)
    # ===================================
    'Healthcare': {
        'pharma': ['JNJ', 'PFE', 'ABBV', 'LLY'],  # Big pharma
        'biotech': ['GILD', 'AMGN'],  # Biotech
        'devices': ['ABT'],  # Medical devices
        'services': []
    },
    
    # ===================================
    # CONSUMER DISCRETIONARY (6 companies)
    # ===================================
    'Consumer_Discretionary': {
        'retail': ['AMZN', 'HD', 'TGT'],  # E-commerce + retail
        'automotive': ['TSLA', 'F'],  # EV + traditional
        'restaurants': ['MCD'],  # QSR
        'apparel': []
    },
    
    # ===================================
    # CONSUMER STAPLES (4 companies)
    # ===================================
    'Consumer_Staples': {
        'beverages': ['KO', 'PEP'],  # Beverages
        'food': ['PG'],  # Consumer products
        'tobacco': ['PM'],  # Tobacco
        'retail': []
    },
    
    # ===================================
    # INDUSTRIALS (5 companies)
    # ===================================
    'Industrials': {
        'aerospace': ['BA', 'LMT'],  # Aerospace & defense
        'machinery': ['CAT', 'DE'],  # Heavy machinery
        'transportation': ['UPS'],  # Logistics
        'conglomerates': []
    },
    
    # ===================================
    # ENERGY (4 companies)
    # ===================================
    'Energy': {
        'integrated': ['XOM', 'CVX'],  # Integrated oil & gas
        'exploration': ['COP', 'EOG'],  # E&P
        'services': [],
        'renewable': []
    },
    
    # ===================================
    # MATERIALS (2 companies)
    # ===================================
    'Materials': {
        'chemicals': ['LIN'],  # Specialty chemicals
        'metals': ['NUE'],  # Steel
        'mining': []
    },
    
    # ===================================
    # UTILITIES (1 company)
    # ===================================
    'Utilities': {
        'electric': ['NEE'],  # Electric utilities
        'multi': []
    },
    
    # ===================================
    # REAL ESTATE (2 companies)
    # ===================================
    'Real_Estate': {
        'reits': ['PLD', 'AMT'],  # REITs
        'diversified': []
    },
    
    # ===================================
    # COMMUNICATION SERVICES (1 company)
    # ===================================
    'Communication_Services': {
        'telecom': ['T'],  # Telecom
        'media': []
    }
}

# ==========================================
# FLAT LIST FOR TESTING
# ==========================================

def get_all_tickers():
    """Get flat list of all tickers"""
    tickers = []
    for sector, subsectors in EXPANDED_TEST_SET.items():
        for subsector, companies in subsectors.items():
            tickers.extend(companies)
    return sorted(list(set(tickers)))  # Remove duplicates, sort

ALL_TEST_TICKERS = get_all_tickers()

# ==========================================
# SPECIAL CATEGORIES
# ==========================================

# Companies with known-good baseline data
BASELINE_COMPANIES = ['AAPL', 'MSFT', 'JPM', 'JNJ', 'XOM']

# Loss-making companies (for negative earnings tests)
LOSS_MAKING = []  # Will add after initial validation

# High leverage (Debt/Equity > 2)
HIGH_LEVERAGE = ['BA', 'F', 'T']  # Known high-debt companies

# Turnaround situations
TURNAROUNDS = []  # Will identify during validation

# Low liquidity / special situations
SPECIAL_CASES = ['BRK-B']  # Berkshire has unique structure

# ==========================================
# SECTOR MAPPING
# ==========================================

SECTOR_MAP = {}
for sector, subsectors in EXPANDED_TEST_SET.items():
    for subsector, companies in subsectors.items():
        for company in companies:
            SECTOR_MAP[company] = sector

def get_sector(ticker: str) -> str:
    """Get sector for a ticker"""
    return SECTOR_MAP.get(ticker, 'Unknown')

# ==========================================
# TEST CONFIGURATIONS
# ==========================================

# Quick validation (5 companies, one per major sector)
QUICK_TEST = ['AAPL', 'JPM', 'JNJ', 'XOM', 'AMZN']

# Medium validation (20 companies)
MEDIUM_TEST = [
    # Tech
    'AAPL', 'MSFT', 'GOOGL', 'META',
    # Finance
    'JPM', 'BAC', 'BLK',
    # Healthcare
    'JNJ', 'PFE', 'ABBV',
    # Consumer
    'AMZN', 'HD', 'KO', 'PG',
    # Industrial
    'CAT', 'BA',
    # Energy
    'XOM', 'CVX',
    # Other
    'T', 'NEE'
]

# Full validation (all 50)
FULL_TEST = ALL_TEST_TICKERS

# ==========================================
# PRINT SUMMARY
# ==========================================

if __name__ == "__main__":
    print("="*60)
    print("EXPANDED TEST COMPANY SET")
    print("="*60)
    print(f"\nTotal Companies: {len(ALL_TEST_TICKERS)}")
    print(f"Sectors: {len(EXPANDED_TEST_SET)}")
    
    print("\n" + "="*60)
    print("BREAKDOWN BY SECTOR")
    print("="*60)
    
    for sector, subsectors in EXPANDED_TEST_SET.items():
        count = sum(len(companies) for companies in subsectors.values())
        print(f"\n{sector}: {count} companies")
        for subsector, companies in subsectors.items():
            if companies:
                print(f"  - {subsector}: {', '.join(companies)}")
    
    print("\n" + "="*60)
    print("TEST CONFIGURATIONS")
    print("="*60)
    print(f"Quick Test (5 companies): {', '.join(QUICK_TEST)}")
    print(f"Medium Test (20 companies): {len(MEDIUM_TEST)} tickers")
    print(f"Full Test (50 companies): {len(FULL_TEST)} tickers")
    
    print("\n" + "="*60)
    print("SPECIAL CATEGORIES")
    print("="*60)
    print(f"Baseline Companies: {', '.join(BASELINE_COMPANIES)}")
    print(f"High Leverage: {', '.join(HIGH_LEVERAGE)}")
    print(f"Special Cases: {', '.join(SPECIAL_CASES)}")
    
    print("\n" + "="*60)
    print("ALL TICKERS (alphabetical)")
    print("="*60)
    for i in range(0, len(ALL_TEST_TICKERS), 10):
        print(", ".join(ALL_TEST_TICKERS[i:i+10]))


