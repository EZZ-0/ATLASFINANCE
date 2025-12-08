"""
S&P 500 SECTOR MAPPING
================================================================================
Pre-built mapping of S&P 500 tickers to sectors for fast peer discovery.

This avoids calling yfinance.Ticker().info for all 500 companies.

Data Source: S&P 500 Index composition (as of Nov 2025)
Update Frequency: Quarterly or as needed
"""

from typing import List

# Sector mapping: ticker → sector
SP500_SECTOR_MAP = {
    # Technology
    'AAPL': 'Technology', 'MSFT': 'Technology', 'NVDA': 'Technology', 'AVGO': 'Technology',
    'CRM': 'Technology', 'ORCL': 'Technology', 'CSCO': 'Technology', 'ACN': 'Technology',
    'AMD': 'Technology', 'ADBE': 'Technology', 'INTC': 'Technology', 'TXN': 'Technology',
    'QCOM': 'Technology', 'AMAT': 'Technology', 'MU': 'Technology', 'LRCX': 'Technology',
    'KLAC': 'Technology', 'SNPS': 'Technology', 'CDNS': 'Technology', 'MCHP': 'Technology',
    'FTNT': 'Technology', 'ADSK': 'Technology', 'ANSS': 'Technology', 'APH': 'Technology',
    'MSI': 'Technology', 'TEL': 'Technology', 'KEYS': 'Technology', 'IBM': 'Technology',
    'HPQ': 'Technology', 'GLW': 'Technology', 'MPWR': 'Technology', 'NTAP': 'Technology',
    
    # Consumer Discretionary / Communication Services
    'AMZN': 'Consumer Cyclical', 'TSLA': 'Consumer Cyclical', 'HD': 'Consumer Cyclical',
    'MCD': 'Consumer Cyclical', 'NKE': 'Consumer Cyclical', 'SBUX': 'Consumer Cyclical',
    'LOW': 'Consumer Cyclical', 'TJX': 'Consumer Cyclical', 'BKNG': 'Consumer Cyclical',
    'CMG': 'Consumer Cyclical', 'MAR': 'Consumer Cyclical', 'ABNB': 'Consumer Cyclical',
    'GM': 'Consumer Cyclical', 'F': 'Consumer Cyclical', 'ORLY': 'Consumer Cyclical',
    'AZO': 'Consumer Cyclical', 'YUM': 'Consumer Cyclical', 'DG': 'Consumer Cyclical',
    'ROST': 'Consumer Cyclical', 'DHI': 'Consumer Cyclical', 'LEN': 'Consumer Cyclical',
    
    # Communication Services / Media
    'GOOGL': 'Communication Services', 'GOOG': 'Communication Services', 'META': 'Communication Services',
    'NFLX': 'Communication Services', 'DIS': 'Communication Services', 'CMCSA': 'Communication Services',
    'VZ': 'Communication Services', 'T': 'Communication Services', 'TMUS': 'Communication Services',
    'CHTR': 'Communication Services', 'EA': 'Communication Services', 'TTWO': 'Communication Services',
    'LYV': 'Communication Services', 'WBD': 'Communication Services', 'FOXA': 'Communication Services',
    'OMC': 'Communication Services', 'IPG': 'Communication Services',
    
    # Healthcare
    'LLY': 'Healthcare', 'UNH': 'Healthcare', 'JNJ': 'Healthcare', 'ABBV': 'Healthcare',
    'MRK': 'Healthcare', 'TMO': 'Healthcare', 'ABT': 'Healthcare', 'DHR': 'Healthcare',
    'PFE': 'Healthcare', 'BMY': 'Healthcare', 'AMGN': 'Healthcare', 'GILD': 'Healthcare',
    'CVS': 'Healthcare', 'CI': 'Healthcare', 'HUM': 'Healthcare', 'ELV': 'Healthcare',
    'MCK': 'Healthcare', 'COR': 'Healthcare', 'CAH': 'Healthcare', 'BDX': 'Healthcare',
    'SYK': 'Healthcare', 'BSX': 'Healthcare', 'MDT': 'Healthcare', 'ISRG': 'Healthcare',
    'ZTS': 'Healthcare', 'REGN': 'Healthcare', 'VRTX': 'Healthcare', 'BIIB': 'Healthcare',
    
    # Financials
    'BRK.B': 'Financial Services', 'JPM': 'Financial Services', 'V': 'Financial Services',
    'MA': 'Financial Services', 'BAC': 'Financial Services', 'WFC': 'Financial Services',
    'MS': 'Financial Services', 'GS': 'Financial Services', 'SPGI': 'Financial Services',
    'BLK': 'Financial Services', 'C': 'Financial Services', 'AXP': 'Financial Services',
    'SCHW': 'Financial Services', 'CB': 'Financial Services', 'PGR': 'Financial Services',
    'MMC': 'Financial Services', 'AON': 'Financial Services', 'TRV': 'Financial Services',
    'ALL': 'Financial Services', 'AIG': 'Financial Services', 'MET': 'Financial Services',
    'PRU': 'Financial Services', 'AFL': 'Financial Services', 'USB': 'Financial Services',
    'PNC': 'Financial Services', 'TFC': 'Financial Services', 'COF': 'Financial Services',
    
    # Consumer Defensive
    'WMT': 'Consumer Defensive', 'PG': 'Consumer Defensive', 'COST': 'Consumer Defensive',
    'KO': 'Consumer Defensive', 'PEP': 'Consumer Defensive', 'PM': 'Consumer Defensive',
    'MO': 'Consumer Defensive', 'MDLZ': 'Consumer Defensive', 'CL': 'Consumer Defensive',
    'KMB': 'Consumer Defensive', 'GIS': 'Consumer Defensive', 'K': 'Consumer Defensive',
    'HSY': 'Consumer Defensive', 'CHD': 'Consumer Defensive', 'CLX': 'Consumer Defensive',
    'SJM': 'Consumer Defensive', 'CPB': 'Consumer Defensive', 'KHC': 'Consumer Defensive',
    
    # Industrials
    'CAT': 'Industrials', 'BA': 'Industrials', 'HON': 'Industrials', 'RTX': 'Industrials',
    'UNP': 'Industrials', 'UPS': 'Industrials', 'DE': 'Industrials', 'LMT': 'Industrials',
    'GE': 'Industrials', 'MMM': 'Industrials', 'EMR': 'Industrials', 'ETN': 'Industrials',
    'ITW': 'Industrials', 'PH': 'Industrials', 'CARR': 'Industrials', 'OTIS': 'Industrials',
    'PCAR': 'Industrials', 'NSC': 'Industrials', 'CSX': 'Industrials', 'NOC': 'Industrials',
    'LHX': 'Industrials', 'GD': 'Industrials', 'TDG': 'Industrials', 'FDX': 'Industrials',
    
    # Energy
    'XOM': 'Energy', 'CVX': 'Energy', 'COP': 'Energy', 'EOG': 'Energy', 'SLB': 'Energy',
    'PXD': 'Energy', 'MPC': 'Energy', 'PSX': 'Energy', 'VLO': 'Energy', 'OXY': 'Energy',
    'WMB': 'Energy', 'KMI': 'Energy', 'HES': 'Energy', 'BKR': 'Energy', 'HAL': 'Energy',
    
    # Utilities
    'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities', 'D': 'Utilities',
    'AEP': 'Utilities', 'EXC': 'Utilities', 'SRE': 'Utilities', 'XEL': 'Utilities',
    'PCG': 'Utilities', 'ED': 'Utilities', 'WEC': 'Utilities', 'ES': 'Utilities',
    
    # Real Estate
    'PLD': 'Real Estate', 'AMT': 'Real Estate', 'CCI': 'Real Estate', 'EQIX': 'Real Estate',
    'PSA': 'Real Estate', 'WELL': 'Real Estate', 'DLR': 'Real Estate', 'O': 'Real Estate',
    'SBAC': 'Real Estate', 'SPG': 'Real Estate', 'VICI': 'Real Estate', 'AVB': 'Real Estate',
    
    # Materials
    'LIN': 'Basic Materials', 'APD': 'Basic Materials', 'SHW': 'Basic Materials',
    'FCX': 'Basic Materials', 'NEM': 'Basic Materials', 'ECL': 'Basic Materials',
    'DD': 'Basic Materials', 'DOW': 'Basic Materials', 'NUE': 'Basic Materials',
    'VMC': 'Basic Materials', 'MLM': 'Basic Materials', 'ALB': 'Basic Materials',
}


def normalize_sector(sector: str) -> str:
    """Normalize sector names to handle yfinance vs our mapping differences."""
    if not sector:
        return "Unknown"
    
    sector_lower = sector.lower()
    
    # Map common variations to our standard names
    sector_map = {
        'consumer discretionary': 'Consumer Cyclical',
        'consumer cyclical': 'Consumer Cyclical',
        'information technology': 'Technology',
        'financials': 'Financial Services',
        'financial services': 'Financial Services',
        'health care': 'Healthcare',
        'healthcare': 'Healthcare',
        'consumer staples': 'Consumer Defensive',
        'consumer defensive': 'Consumer Defensive',
        'materials': 'Basic Materials',
        'basic materials': 'Basic Materials',
    }
    
    return sector_map.get(sector_lower, sector)


def get_sector_peers(ticker: str, sector: str, max_peers: int = 20) -> List[str]:
    """
    Quickly get peer tickers from the same sector
    
    Args:
        ticker: Primary company ticker
        sector: Sector name (will be normalized)
        max_peers: Max number of peers to return
        
    Returns:
        List of peer tickers
    """
    # Normalize the sector name
    normalized_sector = normalize_sector(sector)
    
    peers = []
    
    for peer_ticker, peer_sector in SP500_SECTOR_MAP.items():
        # Also normalize the mapped sector for comparison
        if peer_ticker != ticker and normalize_sector(peer_sector) == normalized_sector:
            peers.append(peer_ticker)
            
            if len(peers) >= max_peers:
                break
    
    return peers

