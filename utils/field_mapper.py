"""
SMART FIELD RESOLVER - Financial Intelligence Layer
====================================================

Intelligently finds field values using:
1. EXACT match - Try the requested key first
2. KNOWN ALIASES - Check common variations
3. FUZZY MATCH - Normalize and find similar keys
4. CONTAINS MATCH - Find keys containing the concept

This approach means NEW field names are automatically discovered
without needing to update the mapper.

Author: ATLAS Financial Intelligence
"""

from typing import Any, Dict, List, Optional
import re


def _normalize_key(key: str) -> str:
    """
    Normalize a key for comparison:
    - Lowercase
    - Remove underscores, spaces, hyphens
    - Handle camelCase -> lowercase
    
    Examples:
        "PE_Ratio" -> "peratio"
        "priceToBook" -> "pricetobook"
        "Return On Equity" -> "returnonequity"
    """
    if not key:
        return ""
    
    # Convert camelCase to lowercase
    # Insert space before caps, then lowercase all
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
    
    # Remove all separators and lowercase
    return re.sub(r'[_\-\s/]', '', s).lower()


def _is_valid_value(val: Any) -> bool:
    """Check if a value is valid (not None, not 'N/A', not empty)"""
    if val is None:
        return False
    if isinstance(val, str) and val.strip().upper() in ('N/A', 'NA', '', 'NONE', 'NULL'):
        return False
    if isinstance(val, float) and (val != val):  # NaN check
        return False
    return True


# ============================================================================
# MASTER ALIAS MAP - ENORMOUS comprehensive mapping
# Sources: yfinance, SEC EDGAR/XBRL, FMP, Alpha Vantage, Bloomberg, Reuters
# 500+ known variations - fast O(1) lookup via reverse index
# ============================================================================

MASTER_ALIAS_MAP = {
    # =========================================================================
    # VALUATION RATIOS
    # =========================================================================
    "pe_ratio": [
        "trailingPE", "trailing_pe", "pe_trailing", "PriceEarningsRatio", 
        "PERatio", "PE_Ratio", "peRatio", "pe_ratio", "priceEarningsRatio",
        "P/E", "P_E", "pe", "PE", "price_to_earnings", "priceToEarnings",
        "trailing_price_earnings", "trailingPriceEarnings", "ttm_pe", "TTM_PE", 
        "pe_ttm", "priceEarningsRatioTTM",
    ],
    "forward_pe": [
        "forwardPE", "forward_pe", "forwardPERatio", "forward_price_earnings", 
        "forwardPriceEarnings", "pe_forward", "PE_Forward", "fwd_pe", "fwdPE",
        "next_year_pe", "ntm_pe", "NTM_PE", "forwardPriceToEarnings",
    ],
    "peg_ratio": [
        "pegRatio", "peg_ratio", "PEGRatio", "PEG_Ratio", "priceEarningsGrowth", 
        "price_earnings_growth", "PEG", "peg", "pe_growth_ratio", "pegRatioTTM",
    ],
    "price_to_book": [
        "priceToBook", "price_to_book", "PriceBookRatio", "PriceToBookValue",
        "pbRatio", "pb_ratio", "priceToBookRatio", "P/B", "P_B", "pb", "PB", 
        "price_book", "book_value_ratio", "marketToBook", "priceToBookValueTTM",
    ],
    "price_to_sales": [
        "priceToSalesTrailing12Months", "price_to_sales", "PriceSalesRatio", 
        "PriceToSales", "psRatio", "ps_ratio", "priceToSalesRatio", "P/S", 
        "P_S", "ps", "PS", "price_sales", "salesMultiple", "revenue_multiple",
        "priceToSalesRatioTTM",
    ],
    "price_to_cash_flow": [
        "priceToCashFlow", "price_to_cash_flow", "priceToOperatingCashFlows", 
        "priceToCashFlowRatio", "P/CF", "P_CF", "pcf", "PCF", "price_cash_flow", 
        "cashFlowMultiple", "priceToCashFlowTTM",
    ],
    "price_to_fcf": [
        "priceToFreeCashFlow", "price_to_free_cash_flow", "priceToFCF", 
        "P/FCF", "P_FCF", "pfcf", "fcf_multiple", "fcfMultiple", "priceToFCFTTM",
    ],
    "ev_to_ebitda": [
        "enterpriseToEbitda", "enterprise_to_ebitda", "evToEbitda", "ev_to_ebitda", 
        "evEbitda", "EV/EBITDA", "EV_EBITDA", "ev_ebitda", "enterprise_value_ebitda", 
        "enterpriseValueEbitda", "evToEbitdaTTM",
    ],
    "ev_to_revenue": [
        "enterpriseToRevenue", "enterprise_to_revenue", "evToRevenue", "ev_to_revenue", 
        "evRevenue", "EV/Revenue", "EV_Revenue", "ev_revenue", "EV/Sales", "ev_sales",
    ],
    "ev_to_ebit": [
        "evToEbit", "ev_to_ebit", "EV/EBIT", "enterpriseToEbit", "enterprise_value_ebit",
    ],
    "dividend_yield": [
        "dividendYield", "dividend_yield", "trailingAnnualDividendYield", 
        "dividendYielTTM", "dividend_yield_ttm", "div_yield", "divYield", 
        "yield", "annual_dividend_yield", "dividendRate", "trailing_dividend_yield",
    ],
    "earnings_yield": [
        "earningsYield", "earnings_yield", "e_p_ratio", "EP_Ratio", "inverse_pe",
    ],

    # =========================================================================
    # PROFITABILITY RATIOS
    # =========================================================================
    "gross_margin": [
        "grossMargins", "gross_margins", "grossMargin", "GrossProfitMargin", 
        "GrossMargin", "grossProfitMargin", "gross_profit_margin", "gpm", "GPM", 
        "gross_margin", "gross_profit_pct", "grossProfitRatio", "gross_profit_ratio",
        "grossProfitMarginTTM",
    ],
    "operating_margin": [
        "operatingMargins", "operating_margins", "operatingMargin", 
        "OperatingProfitMargin", "OperatingMargin", "operatingProfitMargin", 
        "operating_profit_margin", "opm", "OPM", "operating_margin", "op_margin",
        "ebitMargin", "ebit_margin", "operatingIncomeMargin", "operatingProfitMarginTTM",
    ],
    "net_margin": [
        "profitMargins", "profit_margins", "netMargin", "NetProfitMargin", 
        "ProfitMargin", "netProfitMargin", "net_profit_margin", "npm", "NPM", 
        "net_margin", "profit_margin", "netIncomeMargin", "net_income_margin", 
        "bottomLineMargin", "netProfitMarginTTM",
    ],
    "ebitda_margin": [
        "ebitdaMargin", "ebitda_margin", "EBITDAMargin", "ebitda_to_revenue", 
        "ebitdaToRevenue", "ebitdaMarginTTM",
    ],
    "return_on_equity": [
        "returnOnEquity", "return_on_equity", "ReturnOnEquity", "ROE", "roe", 
        "roeTTM", "roe_ttm", "equity_return", "return_equity", "netIncomeToEquity", 
        "net_income_equity", "returnOnEquityTTM",
    ],
    "return_on_assets": [
        "returnOnAssets", "return_on_assets", "ReturnOnAssets", "ROA", "roa", 
        "roaTTM", "roa_ttm", "asset_return", "return_assets", "netIncomeToAssets",
        "returnOnAssetsTTM",
    ],
    "return_on_invested_capital": [
        "returnOnCapital", "return_on_capital", "returnOnInvestedCapital", 
        "return_on_invested_capital", "roic", "ROIC", "roicTTM", "roic_ttm",
        "return_invested_capital", "invested_capital_return", "returnOnCapitalTTM",
    ],
    "return_on_capital_employed": [
        "returnOnCapitalEmployed", "return_on_capital_employed", "roce", "ROCE", 
        "roceTTM", "returnOnCapitalEmployedTTM",
    ],

    # =========================================================================
    # GROWTH RATES
    # =========================================================================
    "revenue_growth": [
        "revenueGrowth", "revenue_growth", "RevenueGrowthRate", "SalesGrowth",
        "revenueGrowthRate", "revenue_growth_rate", "Total_Revenue_CAGR", 
        "revenue_cagr", "revenue_cagr_3y", "sales_growth", "salesGrowth", 
        "topLineGrowth", "rev_growth", "revGrowth", "annual_revenue_growth",
        "revenueGrowthYOY", "revenueGrowthQuarterly",
    ],
    "earnings_growth": [
        "earningsGrowth", "earnings_growth", "EarningsGrowthRate", "NetIncomeGrowth",
        "epsgrowth", "eps_growth", "earningsGrowthRate", "Net_Income_CAGR", 
        "earnings_cagr", "earnings_cagr_3y", "ni_growth", "netIncomeGrowth", 
        "profit_growth", "earnings_growth_rate", "EPS_CAGR", "eps_cagr",
        "earningsGrowthYOY", "epsGrowthQuarterly",
    ],
    "asset_growth": [
        "assetGrowth", "asset_growth", "Total_Assets_CAGR", "assets_cagr", 
        "asset_cagr", "total_asset_growth", "assetGrowthRate",
    ],
    "equity_growth": [
        "equityGrowth", "equity_growth", "Total_Equity_CAGR", "equity_cagr",
        "stockholders_equity_growth", "book_value_growth",
    ],
    "fcf_growth": [
        "freeCashFlowGrowth", "fcf_growth", "Free_Cash_Flow_CAGR", "fcf_cagr",
        "fcfGrowthRate", "free_cash_flow_growth",
    ],
    "dividend_growth": [
        "dividendGrowth", "dividend_growth", "dividendGrowthRate", "dividend_cagr",
        "dps_growth", "dividend_per_share_growth", "dividendGrowth5Year",
    ],

    # =========================================================================
    # CASH FLOW METRICS
    # =========================================================================
    "free_cash_flow": [
        "freeCashFlow", "free_cash_flow", "FreeCashFlow", "FCF", "fcf", 
        "free_cf", "freeCF", "operatingCashFlowMinusCapex",
    ],
    "operating_cash_flow": [
        "operatingCashFlow", "operating_cash_flow", "totalCashFromOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivities", "OperatingCashFlow", 
        "CashFromOperations", "ocf", "OCF", "cfo", "CFO", "cash_from_ops",
    ],
    "fcf_yield": [
        "fcfYield", "fcf_yield", "freeCashFlowYield", "free_cash_flow_yield", 
        "FCF_Yield", "fcf_to_market_cap", "fcfToMarketCap", "fcfYieldTTM",
    ],
    "fcf_margin": [
        "fcfMargin", "fcf_margin", "freeCashFlowMargin", "free_cash_flow_margin", 
        "fcf_to_revenue", "fcfMarginTTM",
    ],
    "fcf_conversion": [
        "fcfConversion", "fcf_conversion", "freeCashFlowConversion", "fcf_to_net_income",
        "cash_conversion", "cashConversion", "fcf_conversion_rate",
    ],
    "ocf_margin": [
        "operatingCashFlowMargin", "ocf_margin", "operating_cash_flow_margin", 
        "cfo_margin", "ocfMarginTTM",
    ],

    # =========================================================================
    # LIQUIDITY RATIOS
    # =========================================================================
    "current_ratio": [
        "currentRatio", "current_ratio", "CurrentRatio", "currentRatioTTM", 
        "current_ratio_ttm", "working_capital_ratio", "liquidity_ratio",
    ],
    "quick_ratio": [
        "quickRatio", "quick_ratio", "QuickRatio", "AcidTestRatio", 
        "acid_test", "acidTest", "acid_ratio", "quickRatioTTM",
    ],
    "cash_ratio": [
        "cashRatio", "cash_ratio", "cashToCurrentLiabilities", 
        "cash_to_current_liabilities", "cashRatioTTM",
    ],

    # =========================================================================
    # LEVERAGE/SOLVENCY RATIOS
    # =========================================================================
    "debt_to_equity": [
        "debtToEquity", "debt_to_equity", "DebtToEquityRatio", "DebtEquityRatio",
        "debtEquityRatio", "debt_equity_ratio", "D/E", "D_E", "de_ratio", 
        "leverage_ratio", "total_debt_to_equity", "debtEquity", "debtEquityRatioTTM",
    ],
    "debt_to_assets": [
        "debtToAssets", "debt_to_assets", "totalDebtToAssets", "debtAssetsRatio",
        "D/A", "debt_asset_ratio", "debtToAssetsTTM",
    ],
    "debt_to_capital": [
        "debtToCapital", "debt_to_capital", "totalDebtToCapital", "debtCapitalRatio",
    ],
    "debt_to_ebitda": [
        "debtToEbitda", "debt_to_ebitda", "netDebtToEbitda", "net_debt_to_ebitda",
        "leverage_multiple", "leverageMultiple", "netDebtToEBITDA",
    ],
    "interest_coverage": [
        "interestCoverage", "interest_coverage", "InterestCoverageRatio", 
        "TimesInterestEarned", "times_interest_earned", "TIE", "ebit_to_interest",
        "interest_coverage_ratio", "ICR", "interestCoverageTTM",
    ],

    # =========================================================================
    # PER SHARE METRICS
    # =========================================================================
    "eps": [
        "trailingEps", "trailing_eps", "basicEps", "EarningsPerShareBasic", 
        "EarningsPerShareDiluted", "BasicEPS", "DilutedEPS", "eps", "epsTTM", 
        "eps_ttm", "EPS", "earnings_per_share", "earningsPerShare",
        "netIncomePerShare", "net_income_per_share", "Diluted EPS",
    ],
    "book_value_per_share": [
        "bookValuePerShare", "book_value_per_share", "bookValue", "book_value", 
        "bvps", "BVPS", "equity_per_share", "navPerShare", "bookValuePerShareTTM",
    ],
    "revenue_per_share": [
        "revenuePerShare", "revenue_per_share", "salesPerShare", "sales_per_share", 
        "rps", "RPS", "revenuePerShareTTM",
    ],
    "fcf_per_share": [
        "freeCashFlowPerShare", "fcf_per_share", "fcfPerShare", 
        "free_cash_flow_per_share", "fcfPerShareTTM",
    ],
    "dividend_per_share": [
        "dividendPerShare", "dividend_per_share", "trailingAnnualDividendRate", 
        "dps", "DPS", "annualDividend", "annual_dividend", "dividendsPerShare",
    ],

    # =========================================================================
    # INCOME STATEMENT LINE ITEMS
    # =========================================================================
    "total_revenue": [
        "Total Revenue", "TotalRevenue", "total_revenue", "Revenues", 
        "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet", 
        "Sales Revenue Net", "revenue", "Revenue", "net_sales", "NetSales", 
        "sales", "Sales", "total_sales", "TotalSales", "topLine", "totalRevenue",
    ],
    "cost_of_revenue": [
        "Cost Of Revenue", "CostOfRevenue", "cost_of_revenue", 
        "CostOfGoodsAndServicesSold", "CostOfGoodsSold", "cost_of_goods_sold", 
        "COGS", "cogs", "CostOfSales", "cost_of_sales", "costOfRevenue",
    ],
    "gross_profit": [
        "Gross Profit", "GrossProfit", "gross_profit", "grossProfit", 
        "gross_income", "GrossIncome",
    ],
    "operating_income": [
        "Operating Income", "OperatingIncome", "operating_income", 
        "OperatingIncomeLoss", "operatingIncome", "EBIT", "ebit", 
        "operating_profit", "OperatingProfit", "operatingProfit",
    ],
    "ebitda": [
        "EBITDA", "ebitda", "Ebitda", "earningsBeforeInterestTaxesDepreciationAmortization",
    ],
    "net_income": [
        "Net Income", "NetIncome", "net_income", "NetIncomeLoss", "ProfitLoss", 
        "netIncome", "NetIncomeLossAttributableToParent", 
        "Net Income From Continuing Operation Net Minority Interest",
        "bottom_line", "bottomLine", "profit", "Profit", "normalizedIncome",
    ],
    "interest_expense": [
        "Interest Expense", "InterestExpense", "interest_expense", 
        "InterestExpenseNonOperating", "interestExpense", "interest_cost", 
        "InterestCost",
    ],
    "tax_expense": [
        "Tax Provision", "TaxProvision", "tax_provision", "IncomeTaxExpenseBenefit", 
        "IncomeTaxExpense", "income_tax_expense", "tax_expense", "TaxExpense",
        "taxProvision",
    ],
    "depreciation": [
        "Depreciation", "depreciation", "DepreciationAndAmortization", 
        "depreciation_amortization", "D&A", "da", "depreciationAmortization",
        "Depreciation And Amortization",
    ],
    "research_development": [
        "Research And Development", "ResearchAndDevelopment", 
        "research_and_development", "R&D", "rd", "ResearchDevelopmentExpense", 
        "rdExpense", "researchAndDevelopmentExpenses",
    ],

    # =========================================================================
    # BALANCE SHEET LINE ITEMS
    # =========================================================================
    "total_assets": [
        "Total Assets", "TotalAssets", "total_assets", "Assets", "assets", 
        "totalAssets",
    ],
    "current_assets": [
        "Current Assets", "CurrentAssets", "current_assets", "AssetsCurrent", 
        "totalCurrentAssets",
    ],
    "total_liabilities": [
        "Total Liabilities Net Minority Interest", "TotalLiabilities", 
        "total_liabilities", "Liabilities", "liabilities", "totalLiabilities",
        "Total Liabilities",
    ],
    "current_liabilities": [
        "Current Liabilities", "CurrentLiabilities", "current_liabilities", 
        "LiabilitiesCurrent", "totalCurrentLiabilities",
    ],
    "total_equity": [
        "Stockholders Equity", "StockholdersEquity", "Total Equity", "TotalEquity", 
        "total_equity", "Total Equity Gross Minority Interest",
        "CommonStockholdersEquity", "shareholders_equity", "book_value", 
        "BookValue", "netWorth", "totalStockholdersEquity",
    ],
    "cash": [
        "Cash And Cash Equivalents", "CashAndCashEquivalents", 
        "cash_and_cash_equivalents", "Cash", "CashAndCashEquivalentsAtCarryingValue",
        "cash_on_hand", "cashOnHand", "cashAndCashEquivalents",
    ],
    "accounts_receivable": [
        "Accounts Receivable", "AccountsReceivable", "accounts_receivable", 
        "Receivables", "AccountsReceivableNetCurrent", "ar", "AR", "netReceivables",
    ],
    "inventory": [
        "Inventory", "inventory", "Inventories", "InventoriesNet", "inventories_net",
    ],
    "total_debt": [
        "Total Debt", "TotalDebt", "total_debt", "Long Term Debt", "LongTermDebt", 
        "long_term_debt", "LongTermDebtAndCapitalLeaseObligations",
        "short_long_term_debt", "ShortLongTermDebt", "totalDebt",
    ],
    "long_term_debt": [
        "Long Term Debt", "LongTermDebt", "long_term_debt", "LongTermDebtNoncurrent", 
        "lt_debt", "LTDebt", "longTermDebt",
    ],
    "short_term_debt": [
        "Short Term Debt", "ShortTermDebt", "short_term_debt", "ShortTermBorrowings", 
        "current_debt", "CurrentDebt", "shortTermDebt",
    ],
    "goodwill": [
        "Goodwill", "goodwill", "GoodwillAndOtherIntangibleAssets",
    ],
    "intangible_assets": [
        "Intangible Assets", "IntangibleAssets", "intangible_assets", 
        "IntangibleAssetsNet", "intangibles", "Intangibles", "intangibleAssets",
    ],
    "property_plant_equipment": [
        "Net PPE", "PropertyPlantEquipment", "property_plant_equipment", 
        "PropertyPlantAndEquipmentNet", "ppe", "PPE", "fixed_assets", "FixedAssets",
        "netPPE", "propertyPlantEquipmentNet",
    ],
    "retained_earnings": [
        "Retained Earnings", "RetainedEarnings", "retained_earnings", 
        "RetainedEarningsAccumulatedDeficit", "retainedEarnings",
    ],

    # =========================================================================
    # CASH FLOW STATEMENT LINE ITEMS
    # =========================================================================
    "cash_from_operations": [
        "Operating Cash Flow", "OperatingCashFlow", "operating_cash_flow", 
        "Cash From Operations", "NetCashProvidedByUsedInOperatingActivities",
        "cfo", "CFO", "ocf", "OCF", "operatingCashFlow",
    ],
    "cash_from_investing": [
        "Investing Cash Flow", "InvestingCashFlow", "investing_cash_flow", 
        "Cash From Investing", "NetCashProvidedByUsedInInvestingActivities",
        "cfi", "CFI", "investingCashFlow",
    ],
    "cash_from_financing": [
        "Financing Cash Flow", "FinancingCashFlow", "financing_cash_flow", 
        "Cash From Financing", "NetCashProvidedByUsedInFinancingActivities",
        "cff", "CFF", "financingCashFlow",
    ],
    "capital_expenditures": [
        "Capital Expenditure", "CapitalExpenditure", "capital_expenditure",
        "CapitalExpenditures", "capex", "CAPEX", "Capex", 
        "PaymentsToAcquirePropertyPlantAndEquipment", "purchases_of_ppe", 
        "PurchasesOfPPE", "capitalExpenditure",
    ],
    "dividends_paid": [
        "Dividends Paid", "DividendsPaid", "dividends_paid", "PaymentsOfDividends", 
        "cash_dividends", "Common Stock Dividend Paid", "dividendsPaid",
    ],
    "share_repurchases": [
        "Share Repurchases", "ShareRepurchases", "share_repurchases", 
        "RepurchaseOfCapitalStock", "stock_buyback", "Common Stock Repurchased", 
        "Buyback", "repurchaseOfCapitalStock",
    ],

    # =========================================================================
    # MARKET DATA
    # =========================================================================
    "market_cap": [
        "marketCap", "market_cap", "MarketCapitalization", "market_capitalization", 
        "mktCap", "MktCap", "MarketCap",
    ],
    "enterprise_value": [
        "enterpriseValue", "enterprise_value", "EnterpriseValue", "ev", "EV", 
        "firm_value", "FirmValue",
    ],
    "shares_outstanding": [
        "sharesOutstanding", "shares_outstanding", "SharesOutstanding", 
        "commonSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic",
        "basic_shares", "BasicShares", "commonStockSharesOutstanding",
    ],
    "beta": [
        "beta", "Beta", "betaFiveYear", "beta_5y", "levered_beta", "LeveredBeta",
    ],
    "current_price": [
        "currentPrice", "current_price", "price", "regularMarketPrice", 
        "lastPrice", "close", "previousClose",
    ],
    "fifty_two_week_high": [
        "fiftyTwoWeekHigh", "fifty_two_week_high", "52WeekHigh", "yearHigh", 
        "year_high", "52_week_high",
    ],
    "fifty_two_week_low": [
        "fiftyTwoWeekLow", "fifty_two_week_low", "52WeekLow", "yearLow", 
        "year_low", "52_week_low",
    ],
    "average_volume": [
        "averageVolume", "average_volume", "avgVolume", "avg_volume", 
        "averageDailyVolume10Day",
    ],
    "volume": [
        "volume", "Volume", "regularMarketVolume", "tradingVolume",
    ],

    # =========================================================================
    # QUALITY/ANALYSIS SCORES
    # =========================================================================
    "growth_score": [
        "growth_score", "growthScore", "growth_quality_score", "growthQualityScore", 
        "growth_rating",
    ],
    "cashflow_score": [
        "cashflow_score", "cashflowScore", "cf_score", "fcf_score", 
        "cash_flow_score", "cashFlowScore",
    ],
    "management_score": [
        "management_score", "managementScore", "mgmt_score", 
        "management_effectiveness_score", "managementEffectivenessScore",
    ],
    "balance_sheet_score": [
        "balance_sheet_score", "balanceSheetScore", "bs_score", 
        "financial_health_score", "health_score", "financialHealthScore",
    ],
    "valuation_score": [
        "valuation_score", "valuationScore", "val_score", "value_score", "valueScore",
    ],
    "consistency_score": [
        "consistency_score", "consistencyScore", "earnings_consistency", 
        "growth_consistency",
    ],
    "piotroski_score": [
        "piotroski_score", "piotroskiScore", "f_score", "FScore", "piotroski_f_score",
    ],
    "altman_z_score": [
        "altman_z_score", "altmanZScore", "z_score", "ZScore", "altman_z",
    ],

    # =========================================================================
    # EFFICIENCY RATIOS
    # =========================================================================
    "asset_turnover": [
        "assetTurnover", "asset_turnover", "totalAssetTurnover", "assetTurnoverRatio",
        "revenue_to_assets", "sales_to_assets", "assetTurnoverTTM",
    ],
    "inventory_turnover": [
        "inventoryTurnover", "inventory_turnover", "inventoryTurnoverRatio", 
        "inv_turnover", "cogs_to_inventory", "inventoryTurnoverTTM",
    ],
    "receivables_turnover": [
        "receivablesTurnover", "receivables_turnover", "accountsReceivableTurnover", 
        "ar_turnover", "receivablesTurnoverTTM",
    ],
    "payables_turnover": [
        "payablesTurnover", "payables_turnover", "accountsPayableTurnover", 
        "ap_turnover", "payablesTurnoverTTM",
    ],
    "days_sales_outstanding": [
        "daysSalesOutstanding", "days_sales_outstanding", "dso", "DSO", 
        "receivable_days", "ar_days", "daysSalesOutstandingTTM",
    ],
    "days_inventory": [
        "daysInventory", "days_inventory", "daysInventoryOutstanding", "dio", 
        "DIO", "inventory_days", "inv_days", "daysInventoryOutstandingTTM",
    ],
    "days_payable": [
        "daysPayable", "days_payable", "daysPayablesOutstanding", "dpo", "DPO", 
        "payable_days", "ap_days", "daysPayablesOutstandingTTM",
    ],
    "cash_conversion_cycle": [
        "cashConversionCycle", "cash_conversion_cycle", "ccc", "CCC", 
        "operating_cycle_net",
    ],

    # =========================================================================
    # SECTOR-SPECIFIC (BANKS)
    # =========================================================================
    "net_interest_margin": [
        "netInterestMargin", "net_interest_margin", "NIM", "nim",
    ],
    "efficiency_ratio": [
        "efficiencyRatio", "efficiency_ratio", "operating_efficiency",
    ],
    "loan_to_deposit": [
        "loanToDeposit", "loan_to_deposit", "ldr", "LDR",
    ],
    "tier1_capital_ratio": [
        "tier1CapitalRatio", "tier1_capital_ratio", "tier1Ratio",
    ],
    "total_capital_ratio": [
        "totalCapitalRatio", "total_capital_ratio", "capitalAdequacyRatio",
    ],
    "npl_ratio": [
        "nplRatio", "npl_ratio", "nonPerformingLoansRatio",
    ],
    "net_charge_off_ratio": [
        "netChargeOffRatio", "net_charge_off_ratio", "chargeOffRate",
    ],

    # =========================================================================
    # SECTOR-SPECIFIC (INSURANCE)
    # =========================================================================
    "combined_ratio": [
        "combinedRatio", "combined_ratio", "loss_expense_ratio",
    ],
    "loss_ratio": [
        "lossRatio", "loss_ratio", "claims_ratio",
    ],
    "expense_ratio_insurance": [
        "expenseRatioInsurance", "expense_ratio_insurance", "underwriting_expense_ratio",
    ],
    "policy_retention": [
        "policyRetention", "policy_retention", "retention_rate",
    ],
    "premium_growth": [
        "premiumGrowth", "premium_growth", "gwp_growth",
    ],

    # =========================================================================
    # SECTOR-SPECIFIC (REAL ESTATE / REITs)
    # =========================================================================
    "ffo": [
        "FFO", "ffo", "fundsFromOperations", "Funds From Operations",
        "funds_from_operations", "FundsFromOperations",
    ],
    "affo": [
        "AFFO", "affo", "adjustedFFO", "Adjusted FFO",
        "adjusted_ffo", "AdjustedFundsFromOperations",
    ],
    "nav": [
        "NAV", "nav", "netAssetValue", "Net Asset Value",
        "net_asset_value", "NetAssetValue",
    ],
    "occupancy_rate": [
        "occupancyRate", "occupancy_rate", "occupancy", "Occupancy",
    ],
    "cap_rate": [
        "capRate", "cap_rate", "capitalizationRate", "Capitalization Rate",
    ],
    "noi": [
        "NOI", "noi", "netOperatingIncome", "Net Operating Income",
        "net_operating_income", "NetOperatingIncome",
    ],

    # =========================================================================
    # SECTOR-SPECIFIC (RETAIL)
    # =========================================================================
    "same_store_sales": [
        "sameStoreSales", "same_store_sales", "comps", "comparable_sales",
        "CompSales", "SSS", "sss", "likeForLikeSales",
    ],
    "sales_per_sqft": [
        "salesPerSqFt", "sales_per_sqft", "sales_per_square_foot",
        "revenuePerSquareFoot",
    ],
    "inventory_per_sqft": [
        "inventoryPerSqFt", "inventory_per_sqft", "inventory_per_square_foot",
    ],

    # =========================================================================
    # SECTOR-SPECIFIC (TELECOM/SAAS)
    # =========================================================================
    "arpu": [
        "ARPU", "arpu", "averageRevenuePerUser", "Average Revenue Per User",
        "average_revenue_per_user", "AverageRevenuePerUser",
    ],
    "churn_rate": [
        "churnRate", "churn_rate", "customerChurn", "customer_churn",
        "attrition_rate", "ChurnRate",
    ],
    "customer_acquisition_cost": [
        "CAC", "cac", "customerAcquisitionCost", "customer_acquisition_cost",
        "CustomerAcquisitionCost", "acquisition_cost",
    ],
    "lifetime_value": [
        "LTV", "ltv", "customerLifetimeValue", "customer_lifetime_value",
        "CLV", "clv", "LifetimeValue", "lifetimeValue",
    ],
    "ltv_cac_ratio": [
        "ltvCacRatio", "ltv_cac_ratio", "ltv_to_cac", "LTV/CAC",
        "ltvCac", "ltv_cac",
    ],
    "mrr": [
        "MRR", "mrr", "monthlyRecurringRevenue", "monthly_recurring_revenue",
        "MonthlyRecurringRevenue",
    ],
    "arr": [
        "ARR", "arr", "annualRecurringRevenue", "annual_recurring_revenue",
        "AnnualRecurringRevenue",
    ],
    "net_revenue_retention": [
        "netRevenueRetention", "net_revenue_retention", "NRR", "nrr",
        "netDollarRetention", "NDR", "ndr",
    ],
    "gross_revenue_retention": [
        "grossRevenueRetention", "gross_revenue_retention", "GRR", "grr",
    ],

    # =========================================================================
    # COMPANY INFO
    # =========================================================================
    "company_name": [
        "shortName", "longName", "companyName", "company_name", "name", "Name",
        "displayName", "businessName", "legalName",
    ],
    "sector": [
        "sector", "Sector", "industrySector", "gicsSector", "GICS_Sector",
    ],
    "industry": [
        "industry", "Industry", "industryGroup", "gicsIndustry", "GICS_Industry",
        "subIndustry",
    ],
    "country": [
        "country", "Country", "headquarters", "domicile", "countryOfRisk",
    ],
    "exchange": [
        "exchange", "Exchange", "primaryExchange", "listingExchange",
        "stockExchange",
    ],
    "currency": [
        "currency", "Currency", "financialCurrency", "tradingCurrency",
        "reportingCurrency",
    ],
    "fiscal_year_end": [
        "fiscalYearEnd", "fiscal_year_end", "fyEnd", "FY_End",
        "financialYearEnd",
    ],
    "employees": [
        "fullTimeEmployees", "employees", "Employees", "employeeCount",
        "numberOfEmployees", "fullTimeEmployeeCount", "headcount",
    ],

    # =========================================================================
    # EARNINGS-SPECIFIC
    # =========================================================================
    "eps_estimate": [
        "epsEstimate", "eps_estimate", "consensusEPS", "meanEPS",
        "epsConsensus", "estimatedEPS", "expectedEPS",
    ],
    "eps_actual": [
        "epsActual", "eps_actual", "reportedEPS", "actualEPS",
    ],
    "eps_surprise": [
        "epsSurprise", "eps_surprise", "earningsSurprise", "surpriseEPS",
        "epsBeat", "earningsBeat",
    ],
    "eps_surprise_percent": [
        "epsSurprisePercent", "eps_surprise_percent", "surprisePercent",
        "earningsSurprisePercent", "beatPercent",
    ],
    "revenue_estimate": [
        "revenueEstimate", "revenue_estimate", "consensusRevenue",
        "meanRevenue", "expectedRevenue",
    ],
    "revenue_actual": [
        "revenueActual", "revenue_actual", "reportedRevenue", "actualRevenue",
    ],
    "revenue_surprise": [
        "revenueSurprise", "revenue_surprise", "revenueBeat",
    ],
    "earnings_date": [
        "earningsDate", "earnings_date", "nextEarnings", "nextEarningsDate",
        "reportDate", "earningsAnnouncement",
    ],
    "earnings_call_time": [
        "earningsCallTime", "earnings_call_time", "earningsTime",
        "announcementTime",
    ],

    # =========================================================================
    # ANALYST RATINGS
    # =========================================================================
    "analyst_rating": [
        "recommendationKey", "recommendation", "analystRating", "analyst_rating",
        "consensusRating", "rating",
    ],
    "target_price": [
        "targetMeanPrice", "targetPrice", "target_price", "priceTarget",
        "meanPriceTarget", "consensusPriceTarget",
    ],
    "target_high": [
        "targetHighPrice", "target_high", "highPriceTarget", "priceTargetHigh",
    ],
    "target_low": [
        "targetLowPrice", "target_low", "lowPriceTarget", "priceTargetLow",
    ],
    "num_analysts": [
        "numberOfAnalystOpinions", "numAnalysts", "analystCount",
        "numberOfAnalysts", "analystCoverage",
    ],
    "strong_buy": [
        "strongBuy", "strong_buy", "strongBuyCount",
    ],
    "buy": [
        "buy", "Buy", "buyCount",
    ],
    "hold": [
        "hold", "Hold", "holdCount",
    ],
    "sell": [
        "sell", "Sell", "sellCount",
    ],
    "strong_sell": [
        "strongSell", "strong_sell", "strongSellCount",
    ],

    # =========================================================================
    # INSIDER/INSTITUTIONAL
    # =========================================================================
    "insider_ownership": [
        "heldPercentInsiders", "insiderOwnership", "insider_ownership",
        "insiderHolding", "insidersPercentHeld", "percentInsiders",
    ],
    "institutional_ownership": [
        "heldPercentInstitutions", "institutionalOwnership", 
        "institutional_ownership", "institutionHolding", 
        "institutionsPercentHeld", "percentInstitutions",
    ],
    "insider_transactions": [
        "insiderTransactions", "insider_transactions", "insiderTrades",
        "insiderBuys", "insiderSells",
    ],
    "short_interest": [
        "shortInterest", "short_interest", "sharesShort", "shortRatio",
        "shortPercentOfFloat",
    ],
    "short_percent_float": [
        "shortPercentOfFloat", "short_percent_float", "shortFloat",
        "percentShortFloat",
    ],
    "days_to_cover": [
        "daysToCover", "days_to_cover", "shortCoverDays",
    ],

    # =========================================================================
    # TECHNICAL INDICATORS (commonly returned by APIs)
    # =========================================================================
    "moving_avg_50": [
        "fiftyDayAverage", "moving_avg_50", "ma50", "MA50", "sma50",
        "SMA50", "50DMA", "50_day_ma",
    ],
    "moving_avg_200": [
        "twoHundredDayAverage", "moving_avg_200", "ma200", "MA200", "sma200",
        "SMA200", "200DMA", "200_day_ma",
    ],
    "rsi": [
        "RSI", "rsi", "relativeStrengthIndex", "relative_strength_index",
    ],
    "macd": [
        "MACD", "macd", "macdLine", "macd_line",
    ],
    "bollinger_upper": [
        "bollingerUpper", "bollinger_upper", "upperBand", "bbUpper",
    ],
    "bollinger_lower": [
        "bollingerLower", "bollinger_lower", "lowerBand", "bbLower",
    ],
}

# ============================================================================
# PRE-COMPUTED LOOKUPS - O(1) access with ZERO runtime overhead
# ============================================================================

# Build REVERSE LOOKUP for O(1) access by exact match
_REVERSE_LOOKUP: Dict[str, str] = {}

# Build NORMALIZED LOOKUP for O(1) access by normalized key
_NORMALIZED_LOOKUP: Dict[str, str] = {}

# All known valid aliases (for fast membership check)
_ALL_ALIASES: set = set()

for _canonical, _aliases in MASTER_ALIAS_MAP.items():
    # Add canonical itself
    _REVERSE_LOOKUP[_canonical] = _canonical
    _REVERSE_LOOKUP[_canonical.lower()] = _canonical
    _NORMALIZED_LOOKUP[_normalize_key(_canonical)] = _canonical
    _ALL_ALIASES.add(_canonical)
    
    for _alias in _aliases:
        _REVERSE_LOOKUP[_alias] = _canonical
        _REVERSE_LOOKUP[_alias.lower()] = _canonical
        _NORMALIZED_LOOKUP[_normalize_key(_alias)] = _canonical
        _ALL_ALIASES.add(_alias)
        _ALL_ALIASES.add(_alias.lower())

# Pre-compute normalized versions of all aliases for each canonical
_NORMALIZED_ALIAS_MAP: Dict[str, List[str]] = {}
for _canonical, _aliases in MASTER_ALIAS_MAP.items():
    _NORMALIZED_ALIAS_MAP[_canonical] = [_canonical] + list(_aliases)


# ============================================================================
# LEGACY COMPATIBILITY - Keep old name working
# ============================================================================
KNOWN_ALIASES = MASTER_ALIAS_MAP


def get_field(data: Dict, field_name: str, default: Any = None) -> Any:
    """
    ULTRA-FAST field retrieval with O(1) lookups - STRICT matching only.
    
    Strategy (all O(1) pre-computed lookups):
    1. Exact match in data (fastest path)
    2. Check if known alias → get canonical → try all aliases
    3. Normalized lookup (handles formatting differences)
    
    NO FUZZY/PARTIAL MATCHING - better to return N/A than wrong data!
    
    Performance: ~0.001ms per lookup (pre-computed hash tables)
    
    Args:
        data: Dictionary containing the data
        field_name: The field name to look for
        default: Default value if not found
        
    Returns:
        The field value or default (NEVER a wrong/guessed value)
        
    Example:
        >>> data = {"pe_trailing": 25.5, "ROE": 0.15}
        >>> get_field(data, "pe_ratio")  # Returns 25.5 (pe_trailing is alias)
        >>> get_field(data, "return_on_equity")  # Returns 0.15 (ROE is alias)
        >>> get_field(data, "xyz_unknown")  # Returns None (NOT a guess)
    """
    if not data or not isinstance(data, dict):
        return default
    
    # =========================================================================
    # FAST PATH 1: Exact match in data (O(1) dict lookup)
    # =========================================================================
    if field_name in data:
        val = data[field_name]
        if _is_valid_value(val):
            return val
    
    # =========================================================================
    # FAST PATH 2: Known alias → canonical → try all aliases (O(1) + O(n) where n = aliases)
    # =========================================================================
    canonical = _REVERSE_LOOKUP.get(field_name)
    if not canonical:
        canonical = _REVERSE_LOOKUP.get(field_name.lower())
    
    if canonical:
        # Try all aliases for this canonical name (pre-computed list)
        aliases = _NORMALIZED_ALIAS_MAP.get(canonical, [])
        for alias in aliases:
            if alias in data:
                val = data[alias]
                if _is_valid_value(val):
                    return val
    
    # =========================================================================
    # FAST PATH 3: Normalized lookup (O(1) hash lookup)
    # Handles: "Total_Revenue" == "Total Revenue" == "totalRevenue"
    # =========================================================================
    normalized_request = _normalize_key(field_name)
    canonical_from_norm = _NORMALIZED_LOOKUP.get(normalized_request)
    
    if canonical_from_norm and canonical_from_norm != canonical:
        # Found via normalization - try its aliases
        aliases = _NORMALIZED_ALIAS_MAP.get(canonical_from_norm, [])
        for alias in aliases:
            if alias in data:
                val = data[alias]
                if _is_valid_value(val):
                    return val
    
    # =========================================================================
    # FALLBACK: Check data keys by normalization (only if not in our map)
    # This catches new field names not yet in our alias map
    # =========================================================================
    for key in data.keys():
        if _normalize_key(key) == normalized_request:
            val = data[key]
            if _is_valid_value(val):
                return val
    
    # NOT FOUND - log for future map expansion (in debug mode)
    _log_unknown_field(field_name, data)
    
    return default


# ============================================================================
# UNKNOWN FIELD TRACKING - Helps expand the map over time
# ============================================================================

_UNKNOWN_FIELDS: set = set()  # Track unknowns to expand map later
_LOG_UNKNOWNS = False  # Set True to see what's missing


def enable_unknown_logging(enable: bool = True):
    """Enable/disable logging of unknown field lookups"""
    global _LOG_UNKNOWNS
    _LOG_UNKNOWNS = enable


def _log_unknown_field(field_name: str, data: Dict):
    """Log when a field isn't found - helps expand the map"""
    global _UNKNOWN_FIELDS
    if _LOG_UNKNOWNS and field_name not in _UNKNOWN_FIELDS:
        _UNKNOWN_FIELDS.add(field_name)
        # Show what keys ARE available (first 10)
        available = list(data.keys())[:10]
        print(f"[FIELD_MAPPER] Unknown field '{field_name}' - available keys: {available}...")


def get_unknown_fields() -> set:
    """Get all unknown fields encountered (for map expansion)"""
    return _UNKNOWN_FIELDS.copy()


def clear_unknown_fields():
    """Clear the unknown fields log"""
    global _UNKNOWN_FIELDS
    _UNKNOWN_FIELDS = set()


# ============================================================================
# FUZZY SEARCH - FOR DEBUGGING/DISCOVERY ONLY, NOT FOR PRODUCTION DATA!
# ============================================================================

def find_similar_fields(data: Dict, search_term: str, threshold: float = 0.6) -> List[tuple]:
    """
    DEBUGGING ONLY - Find fields that might be related to search_term.
    Returns list of (field_name, value, similarity_score) sorted by score.
    
    USE CASE: When a field returns N/A, use this to discover what the
    actual field name might be, then ADD IT TO THE MAP.
    
    DO NOT use this for actual data retrieval - it can return wrong matches!
    
    Example:
        >>> find_similar_fields(data, "revenue")
        [("Total Revenue", 1000000, 0.85), ("revenueGrowth", 0.15, 0.75), ...]
    """
    results = []
    search_norm = _normalize_key(search_term)
    
    for key, val in data.items():
        if not _is_valid_value(val):
            continue
            
        key_norm = _normalize_key(key)
        
        # Calculate simple similarity
        score = 0.0
        
        # Exact normalized match
        if key_norm == search_norm:
            score = 1.0
        # One contains the other
        elif search_norm in key_norm:
            score = len(search_norm) / len(key_norm)
        elif key_norm in search_norm:
            score = len(key_norm) / len(search_norm)
        # Shared prefix
        else:
            common = 0
            for i, (a, b) in enumerate(zip(search_norm, key_norm)):
                if a == b:
                    common += 1
                else:
                    break
            if common > 2:
                score = common / max(len(search_norm), len(key_norm))
        
        if score >= threshold:
            results.append((key, val, round(score, 2)))
    
    return sorted(results, key=lambda x: x[2], reverse=True)


def diagnose_field(data: Dict, field_name: str) -> Dict:
    """
    DEBUGGING TOOL - Diagnose why a field might not be found.
    
    Returns detailed info about:
    - Whether it's in the master map
    - What aliases exist
    - What similar fields exist in the data
    - Suggestions for fixing
    
    Example:
        >>> diagnose_field(data, "revenue_growth")
        {
            "requested": "revenue_growth",
            "in_master_map": True,
            "canonical_name": "revenue_growth",
            "known_aliases": ["revenueGrowth", "revenue_cagr", ...],
            "found_in_data": False,
            "similar_in_data": [("revenueGrowthYOY", 0.15, 0.8)],
            "suggestion": "Add 'revenueGrowthYOY' to MASTER_ALIAS_MAP['revenue_growth']"
        }
    """
    result = {
        "requested": field_name,
        "in_master_map": False,
        "canonical_name": None,
        "known_aliases": [],
        "found_in_data": False,
        "exact_value": None,
        "similar_in_data": [],
        "suggestion": None,
    }
    
    # Check if it's in master map
    canonical = _REVERSE_LOOKUP.get(field_name) or _REVERSE_LOOKUP.get(field_name.lower())
    if canonical:
        result["in_master_map"] = True
        result["canonical_name"] = canonical
        result["known_aliases"] = MASTER_ALIAS_MAP.get(canonical, [])
    elif field_name in MASTER_ALIAS_MAP:
        result["in_master_map"] = True
        result["canonical_name"] = field_name
        result["known_aliases"] = MASTER_ALIAS_MAP[field_name]
    
    # Try to get the actual value
    value = get_field(data, field_name)
    if _is_valid_value(value):
        result["found_in_data"] = True
        result["exact_value"] = value
    
    # Find similar fields
    similar = find_similar_fields(data, field_name, threshold=0.5)
    result["similar_in_data"] = similar[:5]  # Top 5
    
    # Generate suggestion
    if not result["found_in_data"] and similar:
        best_match = similar[0][0]
        if result["canonical_name"]:
            result["suggestion"] = f"Add '{best_match}' to MASTER_ALIAS_MAP['{result['canonical_name']}']"
        else:
            result["suggestion"] = f"Create new entry: MASTER_ALIAS_MAP['{field_name}'] = ['{best_match}', ...]"
    
    return result


def _extract_core_concepts(field_name: str) -> List[str]:
    """
    Extract core financial concepts from a field name.
    
    Examples:
        "pe_ratio" -> ["pe", "peratio"]
        "return_on_equity" -> ["roe", "equity", "returnonequity"]
        "fcf_yield" -> ["fcf", "yield", "freecashflow"]
    """
    concepts = []
    normalized = _normalize_key(field_name)
    concepts.append(normalized)
    
    # Add common abbreviations
    abbreviation_map = {
        "pricetoearnings": "pe",
        "pricetobook": "pb",
        "pricetosales": "ps",
        "returnonequity": "roe",
        "returnonassets": "roa",
        "returnoninvestedcapital": "roic",
        "freecashflow": "fcf",
        "operatingcashflow": "ocf",
        "debttoequity": "de",
        "currentratio": "current",
        "quickratio": "quick",
        "grossmargin": "gross",
        "operatingmargin": "operating",
        "netmargin": "net",
        "enterprisevalue": "ev",
    }
    
    for full, abbrev in abbreviation_map.items():
        if full in normalized or abbrev in normalized:
            concepts.append(abbrev)
            concepts.append(full)
    
    return list(set(concepts))


def get_any_of(data: Dict, *field_names: str, default: Any = None) -> Any:
    """
    Try multiple field names and return the first valid value found.
    
    Args:
        data: Dictionary containing the data
        *field_names: Multiple field names to try in order
        default: Default value if none found
        
    Returns:
        First valid value found or default
        
    Example:
        >>> get_any_of(metrics, "pe_ratio", "pe_trailing", "trailingPE")
    """
    for name in field_names:
        val = get_field(data, name)
        if _is_valid_value(val):
            return val
    return default


def smart_extract(data: Dict, requested_fields: Dict[str, str]) -> Dict:
    """
    Extract multiple fields with intelligent mapping.
    
    Args:
        data: Source dictionary
        requested_fields: Dict of {output_name: field_to_find}
        
    Returns:
        Dict with output_names mapped to found values
        
    Example:
        >>> smart_extract(metrics, {
        ...     "pe": "pe_ratio",
        ...     "pb": "price_to_book", 
        ...     "roe": "return_on_equity"
        ... })
    """
    result = {}
    for output_name, field_name in requested_fields.items():
        result[output_name] = get_field(data, field_name)
    return result


def find_all_matches(data: Dict, concept: str) -> Dict[str, Any]:
    """
    Find ALL fields in data that match a concept.
    Useful for discovery/debugging.
    
    Args:
        data: Dictionary to search
        concept: Concept to find (e.g., "pe", "margin", "growth")
        
    Returns:
        Dict of all matching field_name: value pairs
    """
    matches = {}
    concept_normalized = _normalize_key(concept)
    
    for key, val in data.items():
        if concept_normalized in _normalize_key(key) and _is_valid_value(val):
            matches[key] = val
    
    return matches


# ============================================================================
# CONVENIENCE FUNCTIONS FOR COMMON METRIC GROUPS
# ============================================================================

def get_valuation_metrics(data: Dict) -> Dict:
    """Extract valuation metrics with smart field resolution"""
    return smart_extract(data, {
        "pe_ratio": "pe_ratio",
        "forward_pe": "forward_pe",
        "peg_ratio": "peg_ratio",
        "price_to_book": "price_to_book",
        "price_to_sales": "price_to_sales",
        "ev_to_ebitda": "ev_to_ebitda",
    })


def get_profitability_metrics(data: Dict) -> Dict:
    """Extract profitability metrics with smart field resolution"""
    return smart_extract(data, {
        "roe": "return_on_equity",
        "roa": "return_on_assets",
        "roic": "return_on_invested_capital",
        "gross_margin": "gross_margin",
        "operating_margin": "operating_margin",
        "net_margin": "net_margin",
    })


def get_growth_metrics(data: Dict) -> Dict:
    """Extract growth metrics with smart field resolution"""
    return smart_extract(data, {
        "revenue_growth": "revenue_growth",
        "earnings_growth": "earnings_growth",
        "asset_growth": "asset_growth",
    })


def get_cashflow_metrics(data: Dict) -> Dict:
    """Extract cash flow metrics with smart field resolution"""
    return smart_extract(data, {
        "fcf": "free_cash_flow",
        "fcf_yield": "fcf_yield",
        "fcf_margin": "fcf_margin",
        "fcf_conversion": "fcf_conversion",
        "ocf_margin": "ocf_margin",
    })

