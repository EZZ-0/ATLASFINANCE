"""
THE UNIVERSAL MARKET DICTIONARY (V17.0 - "SCORCHED EARTH")
Exhaustive mapping of every known financial term in the Saudi Market (Tadawul).
Covers IFRS, SAMA, SOCPA, and Legacy standards.
"""

# 1. SECTOR SIGNALS (The "Trigger Words")
# If the document contains these, we lock the sector logic.
SECTOR_SIGNALS = {
    "Banking": [
        "special commission income", "gross financing and investment income", 
        "financing and advances", "customer deposits", "tier 1 sukuk", 
        "murabaha", "ijara", "sAMA", "due to banks", "net interest income"
    ],
    "Telecom": [
        "purchase of intangible assets", "spectrum", "telecommunication", 
        "ict", "mobile", "broadband", "average revenue per user", "arpu"
    ],
    "Insurance": [
        "gross written premiums", "reinsurance", "net claims incurred", 
        "insurance revenue", "gwp", "underwriting result", "policyholders"
    ],
    "REIT": [
        "funds from operations", "rental income", "investment properties", 
        "reit", "unitholders", "net asset value", "nav"
    ],
    "Petrochemical": [
        "aramco", "sabic", "saudi aramco", "saudi basic industries",
        "petrochemical", "crude oil", "refining", "upstream", "downstream",
        "oil and gas", "petroleum"
    ],
    "Corporate": [
        "cost of sales", "gross profit", "sales volume", "selling and distribution",
        "inventory", "manufacturing", "production"
    ]
}

# 2. EXTRACTION MAP (The "Dragnet")
# We list EVERY synonym. The Engine will hunt for these in order.
EXTRACTION_MAP = {
    "Banking": {
        "Revenue": [
            # 2024/Modern Terms
            "Gross financing and investment income", 
            "Total operating income", 
            "Total revenue",
            # Legacy/Specific Terms
            "Special commission income",
            "Net special commission income",
            "Total special commission income",
            "Gross special commission income", 
            "Financing and investment income",
            "Commission income",
            "Investment income",
            "Income from financing and investing activities",
            "Net interest income" # Global Standard
        ],
        "Operating_Profit": [
            # The "Real" Profit Line
            "Net income before zakat",
            "Net profit before zakat",
            "Profit for the year before zakat",
            "Income for the year before zakat",
            "Net income for the year before zakat", 
            "Income before zakat and income tax",
            "Profit before zakat",
            "Profit before income tax and zakat",
            # Proxies if specific line missing
            "Total operating profit", 
            "Net financing and investment income"
        ],
        "Growth_Metric": [
            # Cash Flow Signals
            "Net (increase) decrease in financing", 
            "Net change in financing", 
            "Net increase in financing", 
            "Financing and advances",
            "Loans and advances", 
            "Islamic financing and investment products"
        ],
        "Zakat_Base": [
            "Net Adjusted Income",
            "Zakat base",
            "Zakatable base",
            "Zakat-base",
            "Income subject to zakat",
            "Adjusted income for zakat",
            "Zakatable income"
        ],
        "Cash_Flow_Direction": "Invert"
    },
    
    "Insurance": {
        "Revenue": [
            # IFRS 17 (New Standard)
            "Insurance revenue", 
            # IFRS 4 (Old Standard)
            "Gross written premiums", "GWP", "Gross written premiums (GWP)", 
            "Total underwriting revenue", "Gross insurance premiums"
        ],
        "Operating_Profit": [
            "Net result from insurance service",
            "Net income before zakat",
            "Net profit before zakat",
            "Profit for the year before zakat",
            "Net surplus from insurance operations", 
            "Net underwriting income",
            "Profit before zakat"
        ],
        "Growth_Metric": [
            "Purchase of investments", 
            "Net change in investments", 
            "Additions to available-for-sale investments",
            "Purchase of property and equipment"
        ],
        "Zakat_Base": [
            "Zakat base",
            "Net Adjusted Income",
            "Income subject to zakat",
            "Zakatable income"
        ],
        "Cash_Flow_Direction": "Invert"
    },
    
    "REIT": {
        "Revenue": [
            "Rental income", 
            "Total income", 
            "Total revenue", 
            "Income from investment properties", 
            "Operating revenue"
        ],
        "Operating_Profit": [
            "Funds from Operations (FFO)", 
            "Operating profit", 
            "Net income", 
            "Profit for the year"
        ],
        "Growth_Metric": [
            "Purchase of investment properties", 
            "Acquisition of real estate", 
            "Additions to investment properties", 
            "Capital expenditure on properties"
        ],
        "Zakat_Base": ["Zakat base", "Zakatable income"],
        "Cash_Flow_Direction": "Absolute"
    },
    
    "Corporate": {
        "Revenue": [
            "Revenue", 
            "Sales", 
            "Total revenue", 
            "Net sales", 
            "Gross revenue", 
            "Operating revenue", 
            "Revenue from contracts with customers"
        ],
        "Operating_Profit": [
            "Operating profit",
            "Profit from operations",
            "Operating income",
            "Income from operations",
            "Profit before zakat",
            "Net profit before zakat",
            "Profit for the year before zakat",
            "EBIT", 
            "Earnings before interest and taxes"
        ],
        "Growth_Metric": [
            "Capital expenditures", 
            "Additions to property, plant and equipment", 
            "Purchase of property, plant and equipment", 
            "Capex", 
            "Purchase of intangible assets",
            "Payments for property, plant and equipment"
        ],
        "Zakat_Base": [
            "Zakat base",
            "Income subject to zakat",
            "Zakatable base",
            "Net Adjusted Income",
            "Adjusted income for zakat"
        ],
        "Cash_Flow_Direction": "Absolute"
    },
    
    "Telecom": {
        "Revenue": ["Revenues", "Revenue", "Total revenue", "Service revenue"],
        "Operating_Profit": [
            "Operating profit",
            "Profit from operations",
            "Profit before zakat",
            "Net profit before zakat",
            "EBIT"
        ],
        "Growth_Metric": [
            "Purchase of property and equipment", 
            "Additions to capital work in progress",
            "Capital expenditures"
        ],
        "Zakat_Base": [
            "Zakat base",
            "Income subject to zakat",
            "Net Adjusted Income"
        ],
        "Cash_Flow_Direction": "Absolute"
    },
    
    "Petrochemical": {
        "Revenue": [
            "Revenue",
            "Sales",
            "Total revenue",
            "Net sales",
            "Revenue from contracts with customers"
        ],
        "Operating_Profit": [
            "Operating profit",
            "Profit from operations",
            "Operating income",
            "Income from operations",
            "Profit before zakat",
            "Net profit before zakat",
            "Profit for the year before zakat"
        ],
        "Growth_Metric": [
            "Capital expenditures",
            "Additions to property, plant and equipment",
            "Purchase of property, plant and equipment",
            "Capex"
        ],
        "Zakat_Base": [
            "Zakat base",
            "Income subject to zakat",
            "Net Adjusted Income",
            "Zakatable income"
        ],
        "Cash_Flow_Direction": "Absolute"
    }
}

# 3. ZAKAT RULES (The "Sniper" List)
# We list every known Note Number used by major entities to speed up the search.
ZAKAT_RULES = {
    "Banking": {"Note_Priority": ["Note 15", "Note 28", "Note 43", "Note 20", "Note 23"]},
    "Insurance": {"Note_Priority": ["Note 20", "Note 18", "Note 15"]},
    "REIT": {"Note_Priority": ["Note 10", "Note 22"]}, 
    "Corporate": {"Note_Priority": ["Note 8", "Note 20", "Note 31", "Note 15", "Note 25"]},
    "Petrochemical": {"Note_Priority": ["Note 8", "Note 20", "Note 31", "Note 15"]},
    "Telecom": {"Note_Priority": ["Note 20", "Note 15", "Note 25"]}
}

# 4. LOGIC INJECTION (The Brain Implant)
# Universal Rules that apply to any company in that sector.
LOGIC_INJECTION = {
    "Banking": """
    *** UNIVERSAL BANKING RULES ***
    1. REVENUE: It is rarely called 'Revenue'. Look for 'Gross financing and investment income' OR 'Special Commission Income'.
    2. PROFIT: We want the core operational profit. Look for 'Net income before zakat'.
    3. GROWTH: Bank growth is measured by LENDING. Look for 'Net change in financing' in Cash Flows.
    """,
    
    "Insurance": """
    *** UNIVERSAL INSURANCE RULES ***
    1. REVENUE: 'Insurance Revenue' (New IFRS) or 'Gross Written Premiums' (Old IFRS).
    2. PROFIT: 'Net Result from Insurance Service' or 'Net Income Before Zakat'.
    """,
    
    "Corporate": """
    *** UNIVERSAL CORPORATE RULES ***
    1. REVENUE: Standard 'Revenue' or 'Sales'.
    2. PROFIT: 'Operating Profit' or 'Profit from Operations'.
    3. GROWTH: 'Capital Expenditures' (Capex).
    """,
    
    "Telecom": """
    *** UNIVERSAL TELECOM RULES ***
    1. REVENUE: 'Revenue', 'Revenues', or 'Service Revenue'.
    2. PROFIT: 'Operating Profit' or 'Profit from Operations'.
    3. GROWTH: 'Purchase of Property and Equipment' (Capital Expenditures).
    """,
    
    "REIT": """
    *** UNIVERSAL REIT RULES ***
    1. REVENUE: 'Rental Income' or 'Income from Investment Properties'.
    2. PROFIT: 'Funds from Operations (FFO)' or 'Operating Profit'.
    3. GROWTH: 'Purchase of Investment Properties' or 'Acquisition of Real Estate'.
    """,
    
    "Petrochemical": """
    *** UNIVERSAL PETROCHEMICAL RULES ***
    1. REVENUE: 'Revenue' or 'Sales'. For Aramco/Sabic, look for 'Sales' or 'Revenue from contracts'.
    2. PROFIT: 'Operating Profit', 'Profit from Operations', or 'Operating Income'.
    3. GROWTH: 'Capital Expenditures' (Capex).
    4. IDENTITY: If 'Aramco' or 'Sabic' appears, this is Petrochemical, not generic Corporate.
    """
}