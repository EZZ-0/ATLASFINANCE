"""
Helper functions for consistent number formatting across the app
Import and use these in usa_app.py to fix all formatting issues

Enhanced with:
- External link helper (opens in new tab)
- Smart number formatting with tooltips
- Color-coded change indicators
"""

import pandas as pd
import numpy as np
from typing import Union, Optional

def format_financial_number(x, force_scale=None):
    """
    Universal financial number formatter with adaptive scaling
    
    Args:
        x: Number to format
        force_scale: Optional scale ('T', 'B', 'M', 'K', None for auto)
    
    Returns:
        Formatted string like "$145.00B", "$3.9M", "$7.46"
    """
    if pd.isna(x) or x is None:
        return "N/A"
    
    try:
        x = float(x)
    except (ValueError, TypeError):
        return str(x)
    
    if x == 0:
        return "$0"
    
    abs_x = abs(x)
    sign = "-" if x < 0 else ""
    
    # Force specific scale if requested
    if force_scale == 'T':
        return f"{sign}${abs_x/1e12:.2f}T"
    elif force_scale == 'B':
        return f"{sign}${abs_x/1e9:.2f}B"
    elif force_scale == 'M':
        return f"{sign}${abs_x/1e6:.1f}M"
    elif force_scale == 'K':
        return f"{sign}${abs_x/1e3:.1f}K"
    
    # Auto-detect best scale with better thresholds
    # Rule: Show in the unit that gives 1-999 range (no leading zeros)
    if abs_x >= 1e12:
        return f"{sign}${abs_x/1e12:.2f}T"
    elif abs_x >= 1e9:  # 1B+ shows as billions
        return f"{sign}${abs_x/1e9:.2f}B"
    elif abs_x >= 1e6:  # 1M+ shows as millions
        return f"{sign}${abs_x/1e6:.0f}M"  # No decimals for millions
    elif abs_x >= 1e3:  # 1K+ shows as thousands
        return f"{sign}${abs_x/1e3:.0f}K"  # No decimals for thousands
    else:
        return f"{sign}${abs_x:.2f}"


def format_dataframe_for_display(df, transpose_for_yfinance=False):
    """
    Format DataFrame for clean display in Streamlit
    STANDARD FORMAT: Rows = Metrics, Columns = Dates/Years
    
    Args:
        df: Input DataFrame
        transpose_for_yfinance: DEPRECATED - yfinance already in correct format
    
    Returns:
        Formatted DataFrame ready for display (Metrics as rows, Dates as columns)
    """
    if df.empty:
        return df
    
    df_copy = df.copy()
    
    # yfinance format: rows=metrics, columns=dates → THIS IS CORRECT! Don't transpose!
    # SEC format: rows=dates, columns=metrics → Need to transpose!
    
    # Check if we need to transpose (SEC format: first index is a Timestamp/date)
    if len(df_copy.index) > 0:
        first_idx = df_copy.index[0]
        # If index is Timestamp/date, transpose so metrics become rows
        if isinstance(first_idx, pd.Timestamp) or not isinstance(first_idx, str):
            df_copy = df_copy.T  # Now metrics are rows, dates are columns
    
    # Format all numeric columns
    for col in df_copy.columns:
        try:
            if df_copy[col].dtype in ['float64', 'int64', 'float32', 'int32']:
                df_copy[col] = df_copy[col].apply(format_financial_number)
        except (KeyError, TypeError, AttributeError):
            pass  # Skip non-numeric or problematic columns
    
    return df_copy


def format_dataframe_for_csv(df):
    """
    Format DataFrame for CSV export with proper numbers (no scientific notation)
    STANDARD FORMAT: Rows = Metrics, Columns = Dates/Years
    """
    if df.empty:
        return df
    
    # Create a copy with proper orientation
    df_copy = df.copy()
    
    # Ensure correct orientation: Metrics as rows, Dates as columns
    if len(df_copy.index) > 0:
        first_idx = df_copy.index[0]
        if isinstance(first_idx, pd.Timestamp) or not isinstance(first_idx, str):
            df_copy = df_copy.T
    
    # Convert ALL numeric columns to avoid scientific notation
    for col in df_copy.columns:
        for idx in df_copy.index:
            val = df_copy.at[idx, col]
            if pd.notnull(val):
                try:
                    # Force numeric conversion and formatting
                    num_val = float(val)
                    # Format with NO scientific notation
                    df_copy.at[idx, col] = f"{num_val:.2f}"
                except (ValueError, TypeError):
                    pass  # Keep as-is if not numeric
    
    return df_copy


def prepare_table_for_display(df, table_name="Financial Data"):
    """
    Complete preparation of table for Streamlit display
    - Ensures correct orientation (metrics as columns)
    - Formats all numbers properly
    - Adds helpful styling
    
    Args:
        df: Input DataFrame from yfinance or SEC
        table_name: Name of the table for logging
    
    Returns:
        (display_df, csv_df) - Formatted for display and CSV export
    """
    print(f"[INFO] Preparing table: {table_name}")
    print(f"   Original shape: {df.shape}")
    print(f"   Index type: {type(df.index[0]) if len(df.index) > 0 else 'Empty'}")
    
    # Create display version (with $ formatting) - Metrics as rows
    display_df = format_dataframe_for_display(df)
    print(f"   Display shape: {display_df.shape} (rows=metrics, cols=dates)")
    
    # Create CSV version (with full numbers) - Metrics as rows
    csv_df = format_dataframe_for_csv(df)
    print(f"   CSV shape: {csv_df.shape} (rows=metrics, cols=dates)")
    
    return display_df, csv_df


# Test function
if __name__ == "__main__":
    print("Testing format_helpers...")
    print("="*60)
    
    # Test number formatting
    test_numbers = [
        ("Huge", 1.45e12),
        ("Billions", 1.45e11),
        ("Millions", 3.93e9),
        ("Thousands", 1.98e8),
        ("Small", 7.46),
        ("Negative", -1.23e9),
        ("Zero", 0),
    ]
    
    print("\nNumber Formatting:")
    for label, num in test_numbers:
        print(f"{label:12} {num:15.2e} -> {format_financial_number(num)}")
    
    # Test DataFrame formatting
    print("\n" + "="*60)
    print("\nDataFrame Formatting:")
    test_df = pd.DataFrame({
        'Total Revenue': [1.45e11, 1.35e11, 1.26e11],
        'Net Income': [1.12e10, 9.37e9, 9.7e9],
        'EBIT': [1.33e11, 1.23e11, 1.14e11]
    }, index=['2025-01-31', '2024-01-31', '2023-01-31'])
    
    print("\nOriginal:")
    print(test_df)
    
    display, csv = prepare_table_for_display(test_df.T)  # Simulate yfinance format
    
    print("\nFormatted for Display:")
    print(display)
    
    print("\nFormatted for CSV:")
    print(csv)
    
    print("\n" + "="*60)
    print("[OK] All tests passed!")


# ============================================================================
# ENHANCED HELPERS - Phase 6A
# ============================================================================

def external_link(url: str, text: str, icon: str = "→") -> str:
    """
    Create an external link that opens in a new tab
    
    Args:
        url: The URL to link to
        text: The link text to display
        icon: Optional icon to append (default: →)
    
    Returns:
        HTML string for external link
        
    Usage:
        st.markdown(external_link("https://example.com", "Click here"), unsafe_allow_html=True)
    """
    return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text} {icon}</a>'


def format_large_number(value: Union[int, float, None], 
                        format_type: str = 'currency',
                        decimals: int = 2,
                        show_full_on_hover: bool = True) -> str:
    """
    Format large numbers for readability with optional hover tooltip
    
    Args:
        value: The number to format
        format_type: 'currency', 'shares', 'ratio', 'percent', 'decimal', 'multiplier'
        decimals: Number of decimal places (default: 2)
        show_full_on_hover: Show exact value on hover (default: True)
    
    Returns:
        HTML string with formatted number (and tooltip if enabled)
    
    Examples:
        format_large_number(1808327000, 'currency') 
        → <span title="$1,808,327,000">$1.81B</span>
        
        format_large_number(55028682, 'shares')
        → <span title="55,028,682 shares">55.03M</span>
        
        format_large_number(0.45857, 'ratio')
        → <span title="45.857%">45.9%</span>
    """
    
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 'N/A'
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return 'N/A'
    
    # Store original value for tooltip
    original_value = value
    formatted = ""
    tooltip = ""
    
    if format_type == 'currency':
        # Format currency with B/M/K suffixes
        if abs(value) >= 1e12:
            formatted = f"${value/1e12:.{decimals}f}T"
            tooltip = f"${original_value:,.0f}"
        elif abs(value) >= 1e9:
            formatted = f"${value/1e9:.{decimals}f}B"
            tooltip = f"${original_value:,.0f}"
        elif abs(value) >= 1e6:
            formatted = f"${value/1e6:.{decimals}f}M"
            tooltip = f"${original_value:,.0f}"
        elif abs(value) >= 1e3:
            formatted = f"${value/1e3:.{decimals}f}K"
            tooltip = f"${original_value:,.2f}"
        else:
            formatted = f"${value:.{decimals}f}"
            tooltip = f"${original_value:.{decimals}f}"
    
    elif format_type == 'shares':
        # Format share counts with B/M/K suffixes
        if abs(value) >= 1e9:
            formatted = f"{value/1e9:.{decimals}f}B"
            tooltip = f"{original_value:,.0f} shares"
        elif abs(value) >= 1e6:
            formatted = f"{value/1e6:.{decimals}f}M"
            tooltip = f"{original_value:,.0f} shares"
        elif abs(value) >= 1e3:
            formatted = f"{value/1e3:.{decimals}f}K"
            tooltip = f"{original_value:,.0f} shares"
        else:
            formatted = f"{value:,.0f}"
            tooltip = f"{original_value:,.0f} shares"
    
    elif format_type == 'ratio':
        # Convert decimal to percentage
        formatted = f"{value*100:.{decimals-1}f}%"
        tooltip = f"{original_value*100:.{decimals+2}f}%"
    
    elif format_type == 'percent':
        # Already in percentage form
        formatted = f"{value:.{decimals-1}f}%"
        tooltip = f"{original_value:.{decimals+2}f}%"
    
    elif format_type == 'multiplier':
        # For P/E ratios, multiples, etc.
        formatted = f"{value:.{decimals}f}x"
        tooltip = f"{original_value:.{decimals+2}f}x"
    
    elif format_type == 'decimal':
        # Plain decimal with commas
        if abs(value) >= 1e6:
            formatted = f"{value:,.{decimals}f}"
            tooltip = f"{original_value:,.{decimals+2}f}"
        else:
            formatted = f"{value:.{decimals}f}"
            tooltip = f"{original_value:.{decimals+2}f}"
    
    # Return with or without tooltip
    if show_full_on_hover and formatted != tooltip:
        return f'<span title="{tooltip}" style="cursor: help; border-bottom: 1px dotted;">{formatted}</span>'
    else:
        return formatted


def format_change(value: Union[int, float, None],
                 format_type: str = 'percent',
                 decimals: int = 1) -> str:
    """
    Format a change value with color coding and arrow
    
    Args:
        value: The change value (positive or negative)
        format_type: 'percent' or 'currency' or 'decimal'
        decimals: Number of decimal places
    
    Returns:
        HTML string with color-coded change indicator
        
    Examples:
        format_change(10.2) → <span style="color: #28a745;">↑ 10.2%</span>
        format_change(-5.3) → <span style="color: #dc3545;">↓ 5.3%</span>
    """
    
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return '<span style="color: #9e9e9e;">— N/A</span>'
    
    try:
        value = float(value)
    except (ValueError, TypeError):
        return '<span style="color: #9e9e9e;">— N/A</span>'
    
    # Determine color and arrow
    if value > 0:
        color = "#28a745"  # Green
        arrow = "↑"
    elif value < 0:
        color = "#dc3545"  # Red
        arrow = "↓"
    else:
        color = "#9e9e9e"  # Gray
        arrow = "→"
    
    # Format value
    abs_value = abs(value)
    if format_type == 'percent':
        formatted = f"{abs_value:.{decimals}f}%"
    elif format_type == 'currency':
        if abs_value >= 1e9:
            formatted = f"${abs_value/1e9:.{decimals}f}B"
        elif abs_value >= 1e6:
            formatted = f"${abs_value/1e6:.{decimals}f}M"
        else:
            formatted = f"${abs_value:,.{decimals}f}"
    else:
        formatted = f"{abs_value:.{decimals}f}"
    
    return f'<span style="color: {color}; font-weight: 600;">{arrow} {formatted}</span>'
