# Data Sources module for ATLAS Financial Intelligence
# Contains external data integrations (FRED, Damodaran, etc.)

from .damodaran_data import (
    DamodaranData,
    get_damodaran_client,
    get_industry_benchmark,
    GICS_TO_DAMODARAN
)

from .fred_api import (
    FREDClient,
    get_fred_client,
    get_risk_free_rate,
    get_treasury_rate_for_dcf,
    calculate_wacc_with_live_rate
)

from .sector_mapping import (
    get_damodaran_industry,
    get_sector_for_ticker,
    list_all_damodaran_industries,
    GICS_SECTOR_TO_DAMODARAN,
    GICS_INDUSTRY_TO_DAMODARAN,
    TICKER_SECTOR_OVERRIDES
)

from .sector_benchmarks import (
    SectorBenchmarks,
    BenchmarkComparison,
    ComparisonStatus,
    get_sector_benchmarks,
    compare_to_industry,
    enrich_financials_with_benchmarks
)

from .sec_edgar import (
    SECEdgarClient,
    get_client as get_sec_client,
    get_cik,
    get_company_info,
    get_form4_count,
    get_insider_filing_dates
)

__all__ = [
    # Damodaran
    'DamodaranData',
    'get_damodaran_client', 
    'get_industry_benchmark',
    'GICS_TO_DAMODARAN',
    # FRED
    'FREDClient',
    'get_fred_client',
    'get_risk_free_rate',
    'get_treasury_rate_for_dcf',
    'calculate_wacc_with_live_rate',
    # Sector Mapping
    'get_damodaran_industry',
    'get_sector_for_ticker',
    'list_all_damodaran_industries',
    'GICS_SECTOR_TO_DAMODARAN',
    'GICS_INDUSTRY_TO_DAMODARAN',
    'TICKER_SECTOR_OVERRIDES',
    # Sector Benchmarks
    'SectorBenchmarks',
    'BenchmarkComparison',
    'ComparisonStatus',
    'get_sector_benchmarks',
    'compare_to_industry',
    'enrich_financials_with_benchmarks',
    # SEC EDGAR
    'SECEdgarClient',
    'get_sec_client',
    'get_cik',
    'get_company_info',
    'get_form4_count',
    'get_insider_filing_dates'
]
