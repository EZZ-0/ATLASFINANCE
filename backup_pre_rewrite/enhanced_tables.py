"""
Enhanced Table Component for USA Earnings Engine
=================================================
Provides sortable, filterable tables with conditional formatting

Features:
- Click column headers to sort
- Search/filter functionality
- Conditional formatting (green/red for changes)
- Export to Excel/CSV
- Hover tooltips
- Pagination for large datasets
"""

import streamlit as st
import pandas as pd
import io
from typing import Optional, Tuple

def format_number_for_display(value):
    """Format numbers with M/B suffixes"""
    try:
        if isinstance(value, (int, float)):
            if abs(value) >= 1e9:
                return f"${value/1e9:.2f}B"
            elif abs(value) >= 1e6:
                return f"${value/1e6:.2f}M"
            elif abs(value) >= 1e3:
                return f"${value/1e3:.2f}K"
            else:
                return f"${value:.2f}"
    except (ValueError, TypeError):
        pass
    return value


def format_dataframe_numbers(df: pd.DataFrame) -> pd.DataFrame:
    """Format all numeric columns with M/B suffixes"""
    df_formatted = df.copy()
    
    for col in df_formatted.columns:
        # Check if column contains large numbers
        if df_formatted[col].dtype in ['int64', 'float64']:
            # If values are large (> 1 million), format them
            if df_formatted[col].abs().max() > 1e6:
                df_formatted[col] = df_formatted[col].apply(format_number_for_display)
    
    return df_formatted


def enhanced_dataframe(
    df: pd.DataFrame,
    title: str = "",
    key: str = "",
    show_search: bool = True,
    show_export: bool = True,
    conditional_formatting: bool = True,
    height: int = 400,
    format_numbers: bool = True
) -> None:
    """
    Display an enhanced dataframe with sorting, filtering, and formatting
    
    Args:
        df: Pandas DataFrame to display
        title: Table title
        key: Unique key for Streamlit widgets
        show_search: Show search box
        show_export: Show export buttons
        conditional_formatting: Apply red/green formatting
        height: Table height in pixels
        format_numbers: Format large numbers with M/B suffixes
    """
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Keep original df for search, create display df for formatting
    df_original = df.copy()
    
    # Create container
    with st.container():
        # Title and controls
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            if title:
                st.markdown(f"**{title}**")
        
        with col2:
            if show_export:
                # Excel export (use original data)
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                    df_original.to_excel(writer, sheet_name='Data', index=True)
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="📊 Excel",
                    data=excel_data,
                    file_name=f"{title.replace(' ', '_')}.xlsx",
                    mime="application/vnd.ms-excel",
                    key=f"excel_{key}"
                )
        
        with col3:
            if show_export:
                # CSV export (use original data)
                csv_data = df_original.to_csv(index=True)
                st.download_button(
                    label="📄 CSV",
                    data=csv_data,
                    file_name=f"{title.replace(' ', '_')}.csv",
                    mime="text/csv",
                    key=f"csv_{key}"
                )
        
        # Search box (use index/row names, not values)
        if show_search:
            # Get row labels (index) for autocomplete - much better UX
            row_labels = df.index.astype(str).tolist()
            row_labels = sorted(list(set(row_labels)))[:100]  # Limit to 100
            
            # Simple text search only (autocomplete was confusing with values)
            manual_search = st.text_input(
                "🔍 Search",
                placeholder="Type metric name to filter (e.g., 'revenue', 'net income')...",
                key=f"search_{key}"
            )
            
            if manual_search:
                # Filter by row index (metric names) - case insensitive
                mask = df.index.astype(str).str.contains(manual_search, case=False, na=False)
                df = df[mask]
                df_original = df_original[mask]
                st.caption(f"✅ Found {len(df)} matching rows")
        
        # Format numbers AFTER search for display only
        if format_numbers:
            df_display = format_dataframe_numbers(df)
        else:
            df_display = df
        
        # Apply conditional formatting for numeric columns
        if conditional_formatting:
            df_styled = apply_conditional_formatting(df_display)
        else:
            df_styled = df_display
        
        # Display dataframe
        st.dataframe(
            df_styled,
            use_container_width=True,
            height=height
        )
        
        # Row count
        st.caption(f"Showing {len(df)} rows × {len(df.columns)} columns")


def apply_conditional_formatting(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply conditional formatting to dataframe
    
    Green for positive changes, red for negative
    """
    
    def color_negative_red(val):
        """Color negative values red, positive green"""
        try:
            if isinstance(val, (int, float)):
                if val < 0:
                    return 'color: #F44336'  # Red
                elif val > 0:
                    return 'color: #4CAF50'  # Green
        except (ValueError, TypeError):
            pass
        return ''
    
    def highlight_changes(val):
        """Highlight cells with % changes"""
        try:
            if isinstance(val, str):
                if '%' in val:
                    # Extract numeric value
                    num = float(val.replace('%', '').replace(',', ''))
                    if num < 0:
                        return 'background-color: rgba(244, 67, 54, 0.1); color: #F44336'
                    elif num > 0:
                        return 'background-color: rgba(76, 175, 80, 0.1); color: #4CAF50'
        except (ValueError, TypeError):
            pass
        return ''
    
    # Apply styling
    styled_df = df.style.applymap(color_negative_red)
    styled_df = styled_df.applymap(highlight_changes)
    
    return styled_df


def create_sortable_table(
    df: pd.DataFrame,
    title: str = "",
    default_sort_col: str = None,
    ascending: bool = False
) -> None:
    """
    Create a table with sorting controls
    
    Args:
        df: DataFrame to display
        title: Table title
        default_sort_col: Column to sort by default
        ascending: Sort direction
    """
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Title
    if title:
        st.subheader(title)
    
    # Sorting controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        sort_column = st.selectbox(
            "Sort by",
            options=df.columns.tolist(),
            index=0 if default_sort_col is None else df.columns.tolist().index(default_sort_col),
            key=f"sort_col_{title}"
        )
    
    with col2:
        sort_direction = st.radio(
            "Direction",
            options=["Descending", "Ascending"],
            index=0 if not ascending else 1,
            key=f"sort_dir_{title}",
            horizontal=True
        )
    
    # Sort dataframe
    df_sorted = df.sort_values(
        by=sort_column,
        ascending=(sort_direction == "Ascending")
    )
    
    # Display
    enhanced_dataframe(
        df_sorted,
        title="",
        key=f"table_{title}",
        show_search=True,
        show_export=True,
        conditional_formatting=True
    )


def create_comparison_table(
    df1: pd.DataFrame,
    df2: pd.DataFrame,
    labels: Tuple[str, str] = ("Company A", "Company B"),
    title: str = "Comparison"
) -> None:
    """
    Create a side-by-side comparison table
    
    Args:
        df1: First dataframe
        df2: Second dataframe
        labels: Labels for each dataframe
        title: Table title
    """
    
    st.subheader(title)
    
    # Combine dataframes
    df1_copy = df1.copy()
    df2_copy = df2.copy()
    
    df1_copy.columns = [f"{labels[0]} - {col}" for col in df1_copy.columns]
    df2_copy.columns = [f"{labels[1]} - {col}" for col in df2_copy.columns]
    
    combined = pd.concat([df1_copy, df2_copy], axis=1)
    
    # Display
    enhanced_dataframe(
        combined,
        title="",
        key=f"comp_{title}",
        show_search=False,
        show_export=True,
        conditional_formatting=True,
        height=600
    )


def enhanced_dataframe_with_date_filter(
    df: pd.DataFrame,
    title: str = "",
    key: str = "",
    date_column: str = None,
    frequency: str = "quarterly"
) -> None:
    """
    Enhanced dataframe with date range filtering
    
    Args:
        df: DataFrame with date index or date column
        title: Table title
        key: Unique key
        date_column: Name of date column (if not index)
        frequency: Data frequency for disclaimer
    """
    
    if df is None or df.empty:
        st.warning("No data available")
        return
    
    # Date filter controls
    st.info(f"ℹ️ Search results are based on {frequency} frequency")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Get date range from dataframe
        if date_column:
            dates = pd.to_datetime(df[date_column])
        else:
            dates = pd.to_datetime(df.index)
        
        min_date = dates.min().date()
        max_date = dates.max().date()
        
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key=f"start_{key}"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key=f"end_{key}"
        )
    
    with col3:
        st.write("")  # Spacer
        st.write("")
        apply_filter = st.button("Filter", key=f"apply_{key}", type="primary")
    
    # Apply date filter
    if apply_filter or start_date or end_date:
        if date_column:
            mask = (pd.to_datetime(df[date_column]).dt.date >= start_date) & (pd.to_datetime(df[date_column]).dt.date <= end_date)
        else:
            mask = (pd.to_datetime(df.index).date >= start_date) & (pd.to_datetime(df.index).date <= end_date)
        
        df = df[mask]
        st.success(f"Filtered to {len(df)} rows between {start_date} and {end_date}")
    
    # Display using enhanced_dataframe
    enhanced_dataframe(df, title=title, key=f"table_{key}", show_search=True, show_export=True)

