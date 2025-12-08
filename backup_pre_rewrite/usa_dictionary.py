"""
USA GAAP COMPREHENSIVE FINANCIAL DICTIONARY
=============================================
Exhaustive mapping of all financial statement line items used by USA public companies.
Covers GAAP, SEC regulations, and industry-specific variations.

Purpose: Minimize risk of missing any financial items during extraction.
"""

# === 1. REVENUE TERMINOLOGIES ===
# All possible ways companies report top-line revenue
REVENUE_TERMS = [
    # Standard GAAP
    "Revenue", "Revenues", "Total Revenue", "Total Revenues",
    "Net Revenue", "Net Revenues", 
    "Sales", "Net Sales", "Total Sales",
    
    # Modern Standards (ASC 606)
    "Revenue from contracts with customers",
    "Revenue from contract with customer",
    "Revenues from contracts with customers",
    
    # Industry-Specific
    "Operating Revenue", "Operating Revenues",
    "Service Revenue", "Service Revenues",
    "Product Revenue", "Product Sales",
    "Subscription Revenue", "Recurring Revenue",
    
    # Financial Services
    "Interest Income", "Net Interest Income",
    "Interest and Dividend Income",
    "Total Interest Income",
    
    # Tech/SaaS
    "Platform Revenue", "License Revenue",
    "Professional Services Revenue",
    
    # Retail
    "Store Sales", "Comparable Store Sales",
    "Merchandise Sales",
    
    # Energy
    "Oil and Gas Revenue", "Hydrocarbon Revenue",
    
    # Healthcare
    "Patient Service Revenue", "Premium Revenue",
    
    # Real Estate
    "Rental Income", "Lease Revenue"
]

# === 2. COST OF REVENUE / COGS ===
COGS_TERMS = [
    "Cost of Revenue", "Cost of Revenues",
    "Cost of Sales", "Cost of Goods Sold", "COGS",
    "Cost of Products Sold", "Cost of Services",
    "Cost of Product Revenue", "Cost of Service Revenue",
    "Direct Costs", "Production Costs",
    "Cost of Sales and Services",
    "Total Cost of Revenue"
]

# === 3. GROSS PROFIT ===
GROSS_PROFIT_TERMS = [
    "Gross Profit", "Gross Income",
    "Gross Margin", "Total Gross Profit"
]

# === 4. OPERATING EXPENSES ===
OPEX_TERMS = {
    "R&D": [
        "Research and Development", "R&D", "Research and Development Expense",
        "Research and Development Expenses", "Product Development"
    ],
    "SG&A": [
        "Selling, General and Administrative", "SG&A", "Selling General and Administrative",
        "General and Administrative", "G&A", "Selling and Marketing",
        "Sales and Marketing", "Marketing Expense"
    ],
    "Depreciation": [
        "Depreciation and Amortization", "D&A", "Depreciation", "Amortization",
        "Depreciation Expense", "Amortization Expense"
    ],
    "Other_OpEx": [
        "Other Operating Expenses", "Restructuring Charges",
        "Impairment Charges", "Goodwill Impairment"
    ]
}

# === 5. OPERATING INCOME ===
OPERATING_INCOME_TERMS = [
    "Operating Income", "Operating Profit",
    "Income from Operations", "Profit from Operations",
    "Operating Income (Loss)", "EBIT",
    "Earnings Before Interest and Taxes",
    "Total Operating Income"
]

# === 6. NON-OPERATING ITEMS ===
NON_OPERATING_TERMS = {
    "Interest_Expense": [
        "Interest Expense", "Interest Expense, Net",
        "Net Interest Expense", "Interest and Debt Expense",
        "Interest Paid"
    ],
    "Interest_Income": [
        "Interest Income", "Interest and Investment Income",
        "Investment Income", "Other Income"
    ],
    "Other_Income": [
        "Other Income (Expense)", "Other Income, Net",
        "Non-Operating Income", "Gain on Sale of Assets",
        "Foreign Exchange Gain (Loss)"
    ]
}

# === 7. PRE-TAX INCOME ===
PRETAX_INCOME_TERMS = [
    "Income Before Income Taxes", "Income Before Tax",
    "Earnings Before Tax", "EBT", "Pretax Income",
    "Income (Loss) Before Income Taxes",
    "Profit Before Tax", "Earnings Before Income Taxes"
]

# === 8. TAX EXPENSE ===
TAX_TERMS = [
    "Income Tax Expense", "Provision for Income Taxes",
    "Income Taxes", "Tax Expense", "Income Tax Provision",
    "Benefit from Income Taxes", "Income Tax Benefit"
]

# === 9. NET INCOME ===
NET_INCOME_TERMS = [
    "Net Income", "Net Earnings", "Net Profit",
    "Net Income (Loss)", "Net Loss",
    "Net Income Available to Common Shareholders",
    "Net Income Attributable to Common Shareholders",
    "Net Income Attributable to Shareholders",
    "Profit for the Year", "Earnings",
    "Consolidated Net Income"
]

# === 10. BALANCE SHEET - ASSETS ===
ASSET_TERMS = {
    "Cash": [
        "Cash and Cash Equivalents", "Cash", "Cash Equivalents",
        "Cash and Short-Term Investments", "Marketable Securities"
    ],
    "Receivables": [
        "Accounts Receivable", "Trade Receivables", "Receivables",
        "Accounts Receivable, Net", "Trade and Other Receivables"
    ],
    "Inventory": [
        "Inventory", "Inventories", "Merchandise Inventory"
    ],
    "Current_Assets": [
        "Total Current Assets", "Current Assets"
    ],
    "PPE": [
        "Property, Plant and Equipment", "PP&E", "PPE",
        "Property, Plant and Equipment, Net",
        "Net Property, Plant and Equipment"
    ],
    "Intangibles": [
        "Goodwill", "Intangible Assets", "Intangible Assets, Net",
        "Goodwill and Intangible Assets"
    ],
    "Total_Assets": [
        "Total Assets", "Total Assets"
    ]
}

# === 11. BALANCE SHEET - LIABILITIES ===
LIABILITY_TERMS = {
    "Payables": [
        "Accounts Payable", "Trade Payables", "Payables",
        "Accounts Payable and Accrued Liabilities"
    ],
    "Short_Term_Debt": [
        "Short-Term Debt", "Current Portion of Long-Term Debt",
        "Short-Term Borrowings", "Current Debt"
    ],
    "Current_Liabilities": [
        "Total Current Liabilities", "Current Liabilities"
    ],
    "Long_Term_Debt": [
        "Long-Term Debt", "Long Term Debt", "Total Debt",
        "Long-Term Borrowings", "Senior Notes"
    ],
    "Total_Liabilities": [
        "Total Liabilities"
    ]
}

# === 12. EQUITY ===
EQUITY_TERMS = [
    "Total Stockholders' Equity", "Total Shareholders' Equity",
    "Total Equity", "Shareholders' Equity", "Stockholders' Equity",
    "Common Stock", "Retained Earnings", "Additional Paid-In Capital"
]

# === 13. CASH FLOW STATEMENT ===
CASH_FLOW_TERMS = {
    "Operating_CF": [
        "Net Cash Provided by Operating Activities",
        "Cash Flow from Operating Activities",
        "Operating Cash Flow", "Cash from Operations"
    ],
    "Investing_CF": [
        "Net Cash Used in Investing Activities",
        "Cash Flow from Investing Activities",
        "Cash Used for Investing Activities"
    ],
    "Financing_CF": [
        "Net Cash Used in Financing Activities",
        "Cash Flow from Financing Activities",
        "Cash from Financing Activities"
    ],
    "Capex": [
        "Capital Expenditures", "Capex", "Purchase of Property and Equipment",
        "Payments for Property, Plant and Equipment",
        "Purchase of Property, Plant and Equipment"
    ],
    "Free_Cash_Flow": [
        "Free Cash Flow", "FCF"
    ]
}

# === 14. PER-SHARE METRICS ===
PER_SHARE_TERMS = {
    "Basic_EPS": [
        "Basic Earnings Per Share", "Basic EPS",
        "Earnings Per Share - Basic", "EPS Basic"
    ],
    "Diluted_EPS": [
        "Diluted Earnings Per Share", "Diluted EPS",
        "Earnings Per Share - Diluted", "EPS Diluted"
    ],
    "Dividends": [
        "Dividends Per Share", "Cash Dividends Per Share",
        "Dividend Paid Per Share"
    ]
}

# === 15. SHARES OUTSTANDING ===
SHARES_TERMS = [
    "Weighted Average Shares Outstanding - Basic",
    "Weighted Average Shares Outstanding - Diluted",
    "Common Shares Outstanding", "Shares Outstanding",
    "Ordinary Shares in Issue"
]

# === 16. COMPREHENSIVE EXTRACTION MAP ===
# Primary financial metrics with ALL possible terms
EXTRACTION_MAP = {
    "Revenue": REVENUE_TERMS,
    "Cost_of_Revenue": COGS_TERMS,
    "Gross_Profit": GROSS_PROFIT_TERMS,
    "Operating_Income": OPERATING_INCOME_TERMS,
    "Net_Income": NET_INCOME_TERMS,
    "Pretax_Income": PRETAX_INCOME_TERMS,
    "Tax_Expense": TAX_TERMS,
    "Total_Assets": ASSET_TERMS["Total_Assets"],
    "Total_Liabilities": LIABILITY_TERMS["Total_Liabilities"],
    "Total_Equity": EQUITY_TERMS,
    "Operating_Cash_Flow": CASH_FLOW_TERMS["Operating_CF"],
    "Capex": CASH_FLOW_TERMS["Capex"],
    "Basic_EPS": PER_SHARE_TERMS["Basic_EPS"],
    "Diluted_EPS": PER_SHARE_TERMS["Diluted_EPS"]
}

# === 17. FINANCIAL RATIOS FORMULAS ===
RATIO_FORMULAS = {
    "Gross_Margin": "Gross_Profit / Revenue * 100",
    "Operating_Margin": "Operating_Income / Revenue * 100",
    "Net_Margin": "Net_Income / Revenue * 100",
    "ROE": "Net_Income / Total_Equity * 100",
    "ROA": "Net_Income / Total_Assets * 100",
    "Current_Ratio": "Current_Assets / Current_Liabilities",
    "Debt_to_Equity": "Total_Debt / Total_Equity",
    "Asset_Turnover": "Revenue / Total_Assets",
    "Free_Cash_Flow": "Operating_Cash_Flow - Capex"
}

# === 18. DCF MODEL ASSUMPTIONS ===
DCF_DEFAULTS = {
    "Revenue_Growth_Rate": {
        "Conservative": 0.05,  # 5%
        "Base": 0.10,          # 10%
        "Aggressive": 0.15     # 15%
    },
    "Terminal_Growth_Rate": {
        "Conservative": 0.02,  # 2%
        "Base": 0.025,         # 2.5%
        "Aggressive": 0.03     # 3%
    },
    "Discount_Rate": {
        "Conservative": 0.12,  # 12%
        "Base": 0.10,          # 10%
        "Aggressive": 0.08     # 8%
    },
    "Projection_Years": 5,
    "Tax_Rate": 0.21  # USA corporate tax rate
}

# === 19. INDUSTRY MULTIPLIERS ===
# Used for quick valuation checks
INDUSTRY_MULTIPLES = {
    "Technology": {"P/E": 25, "P/S": 8, "EV/Revenue": 10},
    "Healthcare": {"P/E": 20, "P/S": 4, "EV/Revenue": 5},
    "Financial": {"P/E": 12, "P/B": 1.5, "EV/Assets": 0.15},
    "Consumer": {"P/E": 18, "P/S": 2, "EV/Revenue": 3},
    "Energy": {"P/E": 15, "P/S": 1.5, "EV/Revenue": 2},
    "Industrial": {"P/E": 16, "P/S": 1.8, "EV/Revenue": 2.5},
    "Utilities": {"P/E": 14, "P/B": 1.2, "EV/Assets": 0.8},
    "Real Estate": {"P/FFO": 15, "P/NAV": 1.0}
}

