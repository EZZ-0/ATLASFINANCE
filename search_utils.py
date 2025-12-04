"""
UNIVERSAL SEARCH UTILITY
=========================
Provides search functionality across all extracted financial data.

Features:
- Searches Income Statement, Balance Sheet, Cash Flow metrics
- Searches Ratios, Growth Rates, Market Data
- Returns formatted results with location hints
- Fuzzy matching for better UX
"""

import pandas as pd
from typing import Dict, List, Optional
import re


def build_search_index(financials: Dict) -> List[Dict]:
    """
    Build a searchable index from all financial data.
    
    Indexes:
    - Income Statement metrics
    - Balance Sheet metrics  
    - Cash Flow metrics
    - Financial Ratios
    - Growth Rates
    - Market Data
    - Company Info
    
    Returns:
        List of searchable items with metric, value, category, location
    """
    index = []
    
    if not financials:
        return index
    
    # 1. Income Statement metrics
    income = financials.get("income_statement", pd.DataFrame())
    if not income.empty:
        for metric_name in income.index:
            try:
                # Get latest year value (first column in yfinance format)
                value = income.loc[metric_name].iloc[0] if len(income.columns) > 0 else None
                if pd.notna(value):
                    index.append({
                        "metric": str(metric_name),
                        "value": value,
                        "category": "Income Statement",
                        "location": "Data Tab → Income Statement",
                        "icon": "📊"
                    })
            except (KeyError, TypeError, AttributeError):
                pass  # Metric not found in income statement
    
    # 2. Balance Sheet metrics
    balance = financials.get("balance_sheet", pd.DataFrame())
    if not balance.empty:
        for metric_name in balance.index:
            try:
                value = balance.loc[metric_name].iloc[0] if len(balance.columns) > 0 else None
                if pd.notna(value):
                    index.append({
                        "metric": str(metric_name),
                        "value": value,
                        "category": "Balance Sheet",
                        "location": "Data Tab → Balance Sheet",
                        "icon": "🏦"
                    })
            except (KeyError, TypeError, AttributeError):
                pass  # Metric not found in balance sheet
    
    # 3. Cash Flow metrics
    cashflow = financials.get("cash_flow", pd.DataFrame())
    if not cashflow.empty:
        for metric_name in cashflow.index:
            try:
                value = cashflow.loc[metric_name].iloc[0] if len(cashflow.columns) > 0 else None
                if pd.notna(value):
                    index.append({
                        "metric": str(metric_name),
                        "value": value,
                        "category": "Cash Flow",
                        "location": "Data Tab → Cash Flow",
                        "icon": "💵"
                    })
            except (KeyError, TypeError, AttributeError):
                pass  # Metric not found in cash flow
    
    # 4. Ratios (from ratios DataFrame)
    ratios = financials.get("ratios", pd.DataFrame())
    if not ratios.empty:
        # Ratios are stored transposed (metric names as index)
        for metric_name in ratios.index:
            try:
                # Skip internal/metadata fields
                if str(metric_name).startswith("_") or "timestamp" in str(metric_name).lower():
                    continue
                value = ratios.loc[metric_name].iloc[0] if len(ratios.columns) > 0 else None
                if pd.notna(value):
                    # Clean up metric name
                    clean_name = str(metric_name).replace("_", " ")
                    index.append({
                        "metric": clean_name,
                        "value": value,
                        "category": "Financial Ratios",
                        "location": "Dashboard or Analysis Tab",
                        "icon": "📈"
                    })
            except (KeyError, TypeError, AttributeError):
                pass  # Ratio not found
    
    # 5. Growth Rates (from growth_rates dict)
    growth = financials.get("growth_rates", {})
    if isinstance(growth, dict):
        for key, value in growth.items():
            # Skip internal/status fields
            if key.startswith("_") or key == "status" or key == "message":
                continue
            try:
                if value is not None:
                    clean_name = str(key).replace("_", " ")
                    index.append({
                        "metric": clean_name,
                        "value": value,
                        "category": "Growth Rates",
                        "location": "Analysis Tab → Growth",
                        "icon": "📊"
                    })
            except (KeyError, TypeError, AttributeError):
                pass  # Growth rate not found
    
    # 6. Market Data
    market = financials.get("market_data", {})
    if isinstance(market, dict):
        market_items = [
            ("Current Price", market.get("current_price"), "Dashboard"),
            ("Market Cap", market.get("market_cap"), "Dashboard"),
            ("Shares Outstanding", market.get("shares_outstanding"), "Dashboard"),
        ]
        for name, value, loc in market_items:
            if value is not None:
                index.append({
                    "metric": name,
                    "value": value,
                    "category": "Market Data",
                    "location": loc,
                    "icon": "💹"
                })
    
    # 7. Company Info
    info = financials.get("info", {})
    if isinstance(info, dict):
        info_fields = [
            ("Sector", info.get("sector")),
            ("Industry", info.get("industry")),
            ("Employees", info.get("fullTimeEmployees")),
            ("Country", info.get("country")),
            ("Website", info.get("website")),
            ("52 Week High", info.get("fiftyTwoWeekHigh")),
            ("52 Week Low", info.get("fiftyTwoWeekLow")),
            ("Beta", info.get("beta")),
            ("Dividend Yield", info.get("dividendYield")),
            ("Forward PE", info.get("forwardPE")),
            ("Trailing PE", info.get("trailingPE")),
            ("Price to Book", info.get("priceToBook")),
            ("EPS (TTM)", info.get("trailingEps")),
            ("Revenue (TTM)", info.get("totalRevenue")),
            ("Profit Margin", info.get("profitMargins")),
            ("Operating Margin", info.get("operatingMargins")),
            ("ROE", info.get("returnOnEquity")),
            ("ROA", info.get("returnOnAssets")),
            ("Debt to Equity", info.get("debtToEquity")),
        ]
        for name, value in info_fields:
            if value is not None:
                index.append({
                    "metric": name,
                    "value": value,
                    "category": "Company Info",
                    "location": "Dashboard or Data Tab",
                    "icon": "ℹ️"
                })
    
    # 8. DCF Results (if available)
    dcf_results = financials.get("dcf_results", {})
    if isinstance(dcf_results, dict):
        for scenario in ["conservative", "base", "aggressive"]:
            if scenario in dcf_results:
                result = dcf_results[scenario]
                index.append({
                    "metric": f"DCF Value ({scenario.capitalize()})",
                    "value": result.get("value_per_share", 0),
                    "category": "DCF Valuation",
                    "location": "Model Tab → DCF",
                    "icon": "🎯"
                })
    
    return index


def format_value(value, metric_name: str = "") -> str:
    """
    Format a value for display based on its type and magnitude.
    
    Args:
        value: The raw value
        metric_name: Name of the metric (helps determine formatting)
        
    Returns:
        Formatted string representation
    """
    if value is None:
        return "N/A"
    
    metric_lower = metric_name.lower()
    
    try:
        if isinstance(value, str):
            return value
        
        if isinstance(value, bool):
            return "Yes" if value else "No"
        
        if isinstance(value, (int, float)):
            # Check if it's a percentage/ratio (value < 1 or contains certain keywords)
            is_ratio = any(term in metric_lower for term in [
                "margin", "ratio", "yield", "roe", "roa", "rate", "growth", 
                "cagr", "pct", "percent", "%"
            ])
            
            is_pe = any(term in metric_lower for term in ["pe", "p/e", "multiple"])
            
            if is_ratio and abs(value) < 10:
                # Format as percentage
                if abs(value) < 1:
                    return f"{value:.1%}"
                else:
                    return f"{value:.1f}%"
            elif is_pe:
                return f"{value:.1f}x"
            elif abs(value) >= 1_000_000_000_000:
                return f"${value/1e12:.2f}T"
            elif abs(value) >= 1_000_000_000:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1_000_000:
                return f"${value/1e6:.2f}M"
            elif abs(value) >= 1_000:
                return f"${value/1e3:.1f}K"
            elif abs(value) < 1 and value != 0:
                return f"{value:.4f}"
            else:
                return f"{value:,.2f}"
        
        return str(value)
    except (ValueError, TypeError):
        return str(value)


def search_financials(financials: Dict, query: str, limit: int = 15) -> List[Dict]:
    """
    Search through financial data for matching metrics.
    
    Args:
        financials: The extracted financial data dict
        query: Search string (min 2 characters)
        limit: Max results to return
    
    Returns:
        List of matching items with:
        - metric: Metric name
        - value: Formatted value
        - raw_value: Original value
        - category: Which section (Income Statement, Ratios, etc.)
        - location: Which tab/subtab to find it
        - icon: Category icon
        - relevance: Search relevance score (lower = better match)
    """
    if not query or len(query) < 2:
        return []
    
    if not financials:
        return []
    
    # Build the search index
    index = build_search_index(financials)
    
    query_lower = query.lower().strip()
    query_words = query_lower.split()
    
    results = []
    
    for item in index:
        metric_lower = item["metric"].lower()
        category_lower = item["category"].lower()
        
        # Calculate relevance score (lower = better)
        relevance = 100  # Default: no match
        
        # Exact match (best)
        if query_lower == metric_lower:
            relevance = 0
        # Starts with query
        elif metric_lower.startswith(query_lower):
            relevance = 10
        # Contains query as whole word
        elif query_lower in metric_lower.split():
            relevance = 20
        # Contains query
        elif query_lower in metric_lower:
            relevance = 30
        # Category match
        elif query_lower in category_lower:
            relevance = 40
        # All query words present
        elif all(word in metric_lower for word in query_words):
            relevance = 50
        # Any query word present
        elif any(word in metric_lower for word in query_words if len(word) >= 3):
            relevance = 60
        else:
            continue  # No match
        
        # Format the value
        formatted_value = format_value(item["value"], item["metric"])
        
        results.append({
            "metric": item["metric"],
            "value": formatted_value,
            "raw_value": item["value"],
            "category": item["category"],
            "location": item["location"],
            "icon": item.get("icon", "📊"),
            "relevance": relevance
        })
    
    # Sort by relevance (best matches first)
    results.sort(key=lambda x: x["relevance"])
    
    return results[:limit]


def get_search_suggestions(financials: Dict) -> List[str]:
    """
    Get popular search suggestions based on available data.
    
    Returns:
        List of suggested search terms
    """
    suggestions = []
    
    if not financials:
        return ["Revenue", "Net Income", "PE Ratio", "ROE", "Market Cap"]
    
    # Add common financial terms that exist in the data
    common_terms = [
        "Revenue", "Net Income", "Gross Profit", "EBIT", "EBITDA",
        "Total Assets", "Total Debt", "Cash",
        "Operating Cash Flow", "Free Cash Flow", "CapEx",
        "PE Ratio", "ROE", "ROA", "Margin", "Growth",
        "Market Cap", "Price", "EPS"
    ]
    
    index = build_search_index(financials)
    metric_names = [item["metric"].lower() for item in index]
    
    for term in common_terms:
        if any(term.lower() in name for name in metric_names):
            suggestions.append(term)
    
    return suggestions[:10]


# Quick test
if __name__ == "__main__":
    # Test with mock data
    test_financials = {
        "income_statement": pd.DataFrame({
            "2024": [100e9, 40e9, 25e9],
            "2023": [90e9, 35e9, 22e9]
        }, index=["Total Revenue", "Gross Profit", "Net Income"]),
        "ratios": pd.DataFrame({
            0: [25.5, 0.15, 0.12]
        }, index=["PE_Ratio", "ROE", "ROA"]),
        "market_data": {
            "current_price": 185.50,
            "market_cap": 2.8e12,
            "shares_outstanding": 15.1e9
        }
    }
    
    print("Testing search...")
    results = search_financials(test_financials, "revenue")
    for r in results:
        print(f"  {r['icon']} {r['metric']}: {r['value']} ({r['category']})")
    
    print("\nTesting PE search...")
    results = search_financials(test_financials, "PE")
    for r in results:
        print(f"  {r['icon']} {r['metric']}: {r['value']} ({r['category']})")

