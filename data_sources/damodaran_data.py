"""
DAMODARAN INDUSTRY DATA MODULE
==============================
Downloads and parses Aswath Damodaran's industry data from NYU Stern.

Data Source: https://pages.stern.nyu.edu/~adamodar/

Available Datasets:
- Industry Betas (levered/unlevered)
- Cost of Capital (WACC by industry)
- Valuation Multiples (P/E, EV/EBITDA, etc.)
- Operating Margins
- Growth Rates

Author: ATLAS Financial Intelligence
Created: 2025-12-07 (TASK-E002)
"""

import os
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import json

# Import centralized logging
try:
    from utils.logging_config import EngineLogger
    _logger = EngineLogger.get_logger("DamodaranData")
except ImportError:
    import logging
    _logger = logging.getLogger("DamodaranData")


# ==========================================
# DAMODARAN DATA URLs (Updated January 2024)
# ==========================================

DAMODARAN_BASE_URL = "https://pages.stern.nyu.edu/~adamodar/pc/datasets"

DAMODARAN_DATASETS = {
    'betas': {
        'url': f"{DAMODARAN_BASE_URL}/betas.xls",
        'description': 'Industry Betas (levered and unlevered)',
        'key_columns': ['Industry Name', 'Unlevered Beta', 'Levered Beta', 'D/E Ratio']
    },
    'wacc': {
        'url': f"{DAMODARAN_BASE_URL}/wacc.xls",
        'description': 'Weighted Average Cost of Capital by Industry',
        'key_columns': ['Industry Name', 'Cost of Equity', 'Cost of Debt', 'WACC']
    },
    'pe_data': {
        'url': f"{DAMODARAN_BASE_URL}/pedata.xls",
        'description': 'P/E Ratios by Industry',
        'key_columns': ['Industry Name', 'Current PE', 'Expected Growth', 'PEG Ratio']
    },
    'margins': {
        'url': f"{DAMODARAN_BASE_URL}/margin.xls",
        'description': 'Operating and Net Margins by Industry',
        'key_columns': ['Industry Name', 'Gross Margin', 'Operating Margin', 'Net Margin']
    },
    'ev_multiples': {
        'url': f"{DAMODARAN_BASE_URL}/vebitda.xls",
        'description': 'EV/EBITDA Multiples by Industry',
        'key_columns': ['Industry Name', 'EV/EBITDA', 'EV/EBIT', 'EV/Sales']
    },
    'roe': {
        'url': f"{DAMODARAN_BASE_URL}/roe.xls",
        'description': 'Return on Equity by Industry',
        'key_columns': ['Industry Name', 'ROE', 'ROA', 'ROC']
    }
}


# ==========================================
# GICS SECTOR TO DAMODARAN MAPPING
# ==========================================

# Maps GICS sectors/industries to Damodaran industry names
GICS_TO_DAMODARAN = {
    # Technology
    'Software': 'Software (System & Application)',
    'Semiconductors': 'Semiconductor',
    'IT Services': 'Information Services',
    'Hardware': 'Computers/Peripherals',
    'Technology Hardware': 'Computers/Peripherals',
    'Electronic Equipment': 'Electronics (Consumer & Office)',
    
    # Healthcare
    'Pharmaceuticals': 'Drugs (Pharmaceutical)',
    'Biotechnology': 'Drugs (Biotechnology)',
    'Health Care Equipment': 'Healthcare Products',
    'Health Care Providers': 'Healthcare Support Services',
    
    # Financials
    'Banks': 'Banks (Regional)',
    'Diversified Banks': 'Banks (Money Center)',
    'Insurance': 'Insurance (General)',
    'Capital Markets': 'Investment Co.',
    'Consumer Finance': 'Financial Svcs. (Non-bank & Insurance)',
    
    # Consumer
    'Retail': 'Retail (General)',
    'Consumer Discretionary': 'Retail (General)',
    'Restaurants': 'Restaurant/Dining',
    'Hotels': 'Hotel/Gaming',
    'Apparel': 'Apparel',
    'Automotive': 'Auto Parts',
    
    # Consumer Staples
    'Consumer Staples': 'Food Processing',
    'Beverages': 'Beverage (Soft)',
    'Food Products': 'Food Processing',
    'Household Products': 'Household Products',
    
    # Industrials
    'Aerospace': 'Aerospace/Defense',
    'Industrial Conglomerates': 'Diversified',
    'Machinery': 'Machinery',
    'Airlines': 'Air Transport',
    'Transportation': 'Transportation',
    
    # Energy
    'Oil & Gas': 'Oil/Gas (Integrated)',
    'Energy': 'Oil/Gas (Integrated)',
    'Oil Equipment': 'Oilfield Svcs/Equip.',
    
    # Materials
    'Chemicals': 'Chemical (Basic)',
    'Metals & Mining': 'Metals & Mining',
    'Materials': 'Chemical (Basic)',
    
    # Real Estate
    'Real Estate': 'REIT',
    'REITs': 'REIT',
    
    # Utilities
    'Utilities': 'Utility (General)',
    'Electric Utilities': 'Utility (General)',
    
    # Communication
    'Media': 'Broadcasting',
    'Entertainment': 'Entertainment',
    'Telecom': 'Telecom. Services',
    'Interactive Media': 'Entertainment Tech'
}


class DamodaranData:
    """
    Client for downloading and parsing Damodaran industry data.
    
    Usage:
        damodaran = DamodaranData()
        
        # Get beta for an industry
        beta = damodaran.get_industry_beta("Software")
        
        # Get WACC for an industry
        wacc = damodaran.get_industry_wacc("Banks")
        
        # Get all benchmarks for a sector
        benchmarks = damodaran.get_sector_benchmarks("Technology")
    """
    
    # Cache settings
    CACHE_DIR = "data_sources/cache"
    CACHE_TTL_DAYS = 7  # Refresh weekly (Damodaran updates monthly/yearly)
    
    def __init__(self, cache_dir: Optional[str] = None):
        """Initialize Damodaran data client."""
        self.cache_dir = cache_dir or self.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # In-memory cache for parsed data
        self._data_cache: Dict[str, pd.DataFrame] = {}
        
    # ==========================================
    # DOWNLOAD & CACHING
    # ==========================================
    
    def _get_cache_path(self, dataset_name: str) -> str:
        """Get cache file path for a dataset."""
        return os.path.join(self.cache_dir, f"damodaran_{dataset_name}.parquet")
    
    def _is_cache_valid(self, dataset_name: str) -> bool:
        """Check if cached file exists and is not expired."""
        cache_path = self._get_cache_path(dataset_name)
        if not os.path.exists(cache_path):
            return False
        
        # Check file age
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - file_time > timedelta(days=self.CACHE_TTL_DAYS):
            return False
        
        return True
    
    def _download_dataset(self, dataset_name: str) -> pd.DataFrame:
        """Download dataset from Damodaran's website."""
        if dataset_name not in DAMODARAN_DATASETS:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(DAMODARAN_DATASETS.keys())}")
        
        config = DAMODARAN_DATASETS[dataset_name]
        url = config['url']
        
        _logger.info(f"Downloading Damodaran {dataset_name} from {url}")
        
        try:
            # Download Excel file
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse Excel (usually first sheet has the data)
            # Damodaran files often have header rows we need to skip
            df = pd.read_excel(
                response.content,
                sheet_name=0,
                header=None  # We'll handle headers manually
            )
            
            # Find the header row (usually contains "Industry Name")
            header_row = 0
            for idx, row in df.iterrows():
                if any('industry' in str(cell).lower() for cell in row.values if pd.notna(cell)):
                    header_row = idx
                    break
            
            # Re-read with correct header
            df = pd.read_excel(
                response.content,
                sheet_name=0,
                header=header_row
            )
            
            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]
            
            # Drop empty rows
            df = df.dropna(how='all')
            
            # Cache to parquet
            cache_path = self._get_cache_path(dataset_name)
            df.to_parquet(cache_path, index=False)
            
            _logger.info(f"Downloaded and cached {dataset_name}: {len(df)} industries")
            return df
            
        except Exception as e:
            _logger.error(f"Failed to download {dataset_name}: {e}")
            raise
    
    def get_dataset(self, dataset_name: str, force_refresh: bool = False) -> pd.DataFrame:
        """
        Get a dataset, using cache if available.
        
        Args:
            dataset_name: One of 'betas', 'wacc', 'pe_data', 'margins', 'ev_multiples', 'roe'
            force_refresh: Force download even if cache is valid
            
        Returns:
            DataFrame with industry data
        """
        # Check memory cache first
        if not force_refresh and dataset_name in self._data_cache:
            return self._data_cache[dataset_name]
        
        # Check file cache
        if not force_refresh and self._is_cache_valid(dataset_name):
            cache_path = self._get_cache_path(dataset_name)
            df = pd.read_parquet(cache_path)
            self._data_cache[dataset_name] = df
            return df
        
        # Download fresh
        df = self._download_dataset(dataset_name)
        self._data_cache[dataset_name] = df
        return df
    
    # ==========================================
    # INDUSTRY LOOKUPS
    # ==========================================
    
    def _find_industry(self, df: pd.DataFrame, industry_name: str) -> Optional[pd.Series]:
        """Find industry row by name (fuzzy match)."""
        # First, find the industry name column
        name_col = None
        for col in df.columns:
            if 'industry' in col.lower() and 'name' in col.lower():
                name_col = col
                break
        
        if name_col is None:
            name_col = df.columns[0]  # Assume first column is industry name
        
        # Exact match first
        mask = df[name_col].str.lower().str.strip() == industry_name.lower().strip()
        if mask.any():
            return df[mask].iloc[0]
        
        # Fuzzy match (contains)
        mask = df[name_col].str.lower().str.contains(industry_name.lower().strip(), na=False)
        if mask.any():
            return df[mask].iloc[0]
        
        return None
    
    def get_industry_beta(self, industry_name: str) -> Dict[str, float]:
        """
        Get beta values for an industry.
        
        Returns:
            {
                'unlevered_beta': float,
                'levered_beta': float,
                'd_e_ratio': float
            }
        """
        df = self.get_dataset('betas')
        row = self._find_industry(df, industry_name)
        
        if row is None:
            _logger.warning(f"Industry not found for beta: {industry_name}")
            return {}
        
        result = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'unlever' in col_lower and 'beta' in col_lower:
                result['unlevered_beta'] = self._safe_float(row[col])
            elif 'lever' in col_lower and 'beta' in col_lower:
                result['levered_beta'] = self._safe_float(row[col])
            elif 'd/e' in col_lower or 'debt' in col_lower:
                result['d_e_ratio'] = self._safe_float(row[col])
        
        return result
    
    def get_industry_wacc(self, industry_name: str) -> Dict[str, float]:
        """
        Get WACC components for an industry.
        
        Returns:
            {
                'cost_of_equity': float,
                'cost_of_debt': float,
                'wacc': float
            }
        """
        df = self.get_dataset('wacc')
        row = self._find_industry(df, industry_name)
        
        if row is None:
            _logger.warning(f"Industry not found for WACC: {industry_name}")
            return {}
        
        result = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'equity' in col_lower and 'cost' in col_lower:
                result['cost_of_equity'] = self._safe_float(row[col])
            elif 'debt' in col_lower and 'cost' in col_lower:
                result['cost_of_debt'] = self._safe_float(row[col])
            elif 'wacc' in col_lower:
                result['wacc'] = self._safe_float(row[col])
        
        return result
    
    def get_industry_multiples(self, industry_name: str) -> Dict[str, float]:
        """
        Get valuation multiples for an industry.
        
        Returns:
            {
                'pe_ratio': float,
                'ev_ebitda': float,
                'ev_sales': float,
                'peg_ratio': float
            }
        """
        result = {}
        
        # P/E data
        try:
            df_pe = self.get_dataset('pe_data')
            row = self._find_industry(df_pe, industry_name)
            if row is not None:
                for col in df_pe.columns:
                    col_lower = col.lower()
                    if 'current' in col_lower and 'pe' in col_lower:
                        result['pe_ratio'] = self._safe_float(row[col])
                    elif 'peg' in col_lower:
                        result['peg_ratio'] = self._safe_float(row[col])
        except Exception as e:
            _logger.warning(f"Failed to get P/E data: {e}")
        
        # EV multiples
        try:
            df_ev = self.get_dataset('ev_multiples')
            row = self._find_industry(df_ev, industry_name)
            if row is not None:
                for col in df_ev.columns:
                    col_lower = col.lower()
                    if 'ebitda' in col_lower:
                        result['ev_ebitda'] = self._safe_float(row[col])
                    elif 'sales' in col_lower or 'revenue' in col_lower:
                        result['ev_sales'] = self._safe_float(row[col])
        except Exception as e:
            _logger.warning(f"Failed to get EV data: {e}")
        
        return result
    
    def get_industry_margins(self, industry_name: str) -> Dict[str, float]:
        """
        Get margin data for an industry.
        
        Returns:
            {
                'gross_margin': float,
                'operating_margin': float,
                'net_margin': float
            }
        """
        df = self.get_dataset('margins')
        row = self._find_industry(df, industry_name)
        
        if row is None:
            _logger.warning(f"Industry not found for margins: {industry_name}")
            return {}
        
        result = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'gross' in col_lower:
                result['gross_margin'] = self._safe_float(row[col])
            elif 'operating' in col_lower or 'ebit' in col_lower:
                result['operating_margin'] = self._safe_float(row[col])
            elif 'net' in col_lower:
                result['net_margin'] = self._safe_float(row[col])
        
        return result
    
    def get_industry_profitability(self, industry_name: str) -> Dict[str, float]:
        """
        Get profitability metrics for an industry.
        
        Returns:
            {
                'roe': float,
                'roa': float,
                'roic': float
            }
        """
        df = self.get_dataset('roe')
        row = self._find_industry(df, industry_name)
        
        if row is None:
            _logger.warning(f"Industry not found for ROE: {industry_name}")
            return {}
        
        result = {}
        for col in df.columns:
            col_lower = col.lower()
            if 'roe' in col_lower:
                result['roe'] = self._safe_float(row[col])
            elif 'roa' in col_lower:
                result['roa'] = self._safe_float(row[col])
            elif 'roc' in col_lower or 'roic' in col_lower:
                result['roic'] = self._safe_float(row[col])
        
        return result
    
    # ==========================================
    # COMPREHENSIVE BENCHMARKS
    # ==========================================
    
    def get_all_benchmarks(self, industry_name: str) -> Dict[str, any]:
        """
        Get all available benchmarks for an industry.
        
        Args:
            industry_name: Industry name (can be GICS or Damodaran)
            
        Returns:
            Dictionary with all available benchmarks
        """
        # Try to map GICS to Damodaran if needed
        damodaran_name = GICS_TO_DAMODARAN.get(industry_name, industry_name)
        
        return {
            'industry': damodaran_name,
            'betas': self.get_industry_beta(damodaran_name),
            'wacc': self.get_industry_wacc(damodaran_name),
            'multiples': self.get_industry_multiples(damodaran_name),
            'margins': self.get_industry_margins(damodaran_name),
            'profitability': self.get_industry_profitability(damodaran_name)
        }
    
    def get_sector_benchmarks_for_ticker(self, sector: str, gics_industry: Optional[str] = None) -> Dict:
        """
        Get benchmarks for a company based on its sector/industry.
        
        Args:
            sector: GICS sector (e.g., "Technology", "Healthcare")
            gics_industry: Optional GICS industry for more specific match
            
        Returns:
            Dictionary with all benchmarks
        """
        # Use industry if available, otherwise sector
        lookup_name = gics_industry if gics_industry else sector
        return self.get_all_benchmarks(lookup_name)
    
    # ==========================================
    # UTILITIES
    # ==========================================
    
    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert value to float."""
        if pd.isna(value):
            return None
        try:
            # Handle percentages
            if isinstance(value, str):
                value = value.replace('%', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def list_industries(self, dataset: str = 'betas') -> List[str]:
        """List all available industries in a dataset."""
        df = self.get_dataset(dataset)
        name_col = df.columns[0]
        return df[name_col].dropna().tolist()
    
    def refresh_all_data(self):
        """Force refresh all datasets."""
        for dataset_name in DAMODARAN_DATASETS:
            try:
                self._download_dataset(dataset_name)
            except Exception as e:
                _logger.error(f"Failed to refresh {dataset_name}: {e}")


# ==========================================
# SINGLETON INSTANCE
# ==========================================

_damodaran_client: Optional[DamodaranData] = None

def get_damodaran_client() -> DamodaranData:
    """Get or create singleton Damodaran client."""
    global _damodaran_client
    if _damodaran_client is None:
        _damodaran_client = DamodaranData()
    return _damodaran_client


# ==========================================
# CONVENIENCE FUNCTIONS
# ==========================================

def get_industry_benchmark(industry: str, metric: str) -> Optional[float]:
    """
    Quick lookup for a single benchmark metric.
    
    Args:
        industry: Industry name
        metric: One of 'beta', 'wacc', 'pe', 'operating_margin', 'roe'
        
    Returns:
        Metric value or None
    """
    client = get_damodaran_client()
    
    metric_map = {
        'beta': ('betas', 'levered_beta'),
        'unlevered_beta': ('betas', 'unlevered_beta'),
        'wacc': ('wacc', 'wacc'),
        'cost_of_equity': ('wacc', 'cost_of_equity'),
        'pe': ('multiples', 'pe_ratio'),
        'ev_ebitda': ('multiples', 'ev_ebitda'),
        'operating_margin': ('margins', 'operating_margin'),
        'net_margin': ('margins', 'net_margin'),
        'roe': ('profitability', 'roe'),
        'roa': ('profitability', 'roa')
    }
    
    if metric not in metric_map:
        return None
    
    category, key = metric_map[metric]
    
    if category == 'betas':
        data = client.get_industry_beta(industry)
    elif category == 'wacc':
        data = client.get_industry_wacc(industry)
    elif category == 'multiples':
        data = client.get_industry_multiples(industry)
    elif category == 'margins':
        data = client.get_industry_margins(industry)
    elif category == 'profitability':
        data = client.get_industry_profitability(industry)
    else:
        return None
    
    return data.get(key)


# ==========================================
# TEST / EXAMPLE
# ==========================================

if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("DAMODARAN DATA MODULE TEST")
    print("=" * 60)
    
    client = DamodaranData()
    
    # Test with Software industry
    print("\n[TEST] Software Industry Benchmarks:")
    benchmarks = client.get_all_benchmarks("Software")
    print(f"  Beta (Levered): {benchmarks['betas'].get('levered_beta')}")
    print(f"  WACC: {benchmarks['wacc'].get('wacc')}%")
    print(f"  P/E: {benchmarks['multiples'].get('pe_ratio')}")
    print(f"  Operating Margin: {benchmarks['margins'].get('operating_margin')}%")
    print(f"  ROE: {benchmarks['profitability'].get('roe')}%")
    
    # Test GICS mapping
    print("\n[TEST] GICS to Damodaran Mapping:")
    for gics in ['Semiconductors', 'Banks', 'Pharmaceuticals']:
        damodaran = GICS_TO_DAMODARAN.get(gics, gics)
        print(f"  {gics} → {damodaran}")
    
    print("\n[OK] Module ready for integration")

