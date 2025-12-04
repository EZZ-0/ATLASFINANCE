"""
UI COMPONENTS MODULE - GRACEFUL FALLBACK SYSTEM
================================================
Centralized wrapper for optional UI enhancement libraries.
Ensures the app NEVER breaks even if a library fails to install/import.

Libraries wrapped:
1. streamlit-aggrid - Advanced data tables
2. streamlit-echarts - Gauge and chart components
3. lightweight-charts - TradingView-style financial charts
4. streamlit-extras - Utility components
5. pygwalker - Data exploration
6. streamlit-lottie - Loading animations

Usage:
    from ui_components import smart_dataframe, render_gauge, render_price_chart
    
    # These will use enhanced libraries if available, native Streamlit otherwise
    smart_dataframe(df, title="Income Statement")
    render_gauge(score=85, title="Investment Score")
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Union
import json

# ==========================================
# DARK THEME CONFIGURATION
# ==========================================

DARK_THEME = {
    'bg_primary': '#0f1419',
    'bg_secondary': '#1a1f26',
    'bg_card': '#1e2530',
    'bg_hover': '#252d3a',
    'text_primary': '#f0f4f8',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'accent_primary': '#3b82f6',
    'accent_success': '#10b981',
    'accent_warning': '#f59e0b',
    'accent_danger': '#ef4444',
    'border_subtle': 'rgba(148, 163, 184, 0.1)',
}

# ==========================================
# LIBRARY AVAILABILITY FLAGS
# ==========================================

# AgGrid - Advanced Tables
try:
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
    from st_aggrid.shared import ColumnsAutoSizeMode
    AGGRID_AVAILABLE = True
except ImportError:
    AGGRID_AVAILABLE = False

# ECharts - Gauges and Charts
try:
    from streamlit_echarts import st_echarts
    ECHARTS_AVAILABLE = True
except ImportError:
    ECHARTS_AVAILABLE = False

# Lightweight Charts - TradingView style
try:
    from lightweight_charts import Chart
    from lightweight_charts.widgets import StreamlitChart
    LIGHTWEIGHT_CHARTS_AVAILABLE = True
except ImportError:
    LIGHTWEIGHT_CHARTS_AVAILABLE = False

# Streamlit Extras - Utilities
try:
    from streamlit_extras.metric_cards import style_metric_cards
    from streamlit_extras.colored_header import colored_header
    from streamlit_extras.stoggle import stoggle
    EXTRAS_AVAILABLE = True
except ImportError:
    EXTRAS_AVAILABLE = False

# PyGWalker - Data Exploration
try:
    import pygwalker as pyg
    from pygwalker.api.streamlit import StreamlitRenderer
    PYGWALKER_AVAILABLE = True
except ImportError:
    PYGWALKER_AVAILABLE = False

# Lottie - Animations
try:
    from streamlit_lottie import st_lottie
    import requests
    LOTTIE_AVAILABLE = True
except ImportError:
    LOTTIE_AVAILABLE = False

# ==========================================
# STATUS REPORT
# ==========================================

def get_library_status() -> Dict[str, bool]:
    """Get availability status of all UI libraries"""
    return {
        'AgGrid (Tables)': AGGRID_AVAILABLE,
        'ECharts (Gauges)': ECHARTS_AVAILABLE,
        'Lightweight Charts': LIGHTWEIGHT_CHARTS_AVAILABLE,
        'Streamlit Extras': EXTRAS_AVAILABLE,
        'PyGWalker': PYGWALKER_AVAILABLE,
        'Lottie (Animations)': LOTTIE_AVAILABLE,
    }

def show_library_status():
    """Display library availability in sidebar (for debugging)"""
    status = get_library_status()
    with st.sidebar.expander("🔧 UI Libraries Status", expanded=False):
        for lib, available in status.items():
            icon = "✅" if available else "❌"
            st.text(f"{icon} {lib}")

# ==========================================
# 1. SMART DATAFRAME (AgGrid with fallback)
# ==========================================

def smart_dataframe(
    df: pd.DataFrame,
    title: Optional[str] = None,
    height: int = 400,
    enable_sorting: bool = True,
    enable_filtering: bool = True,
    enable_search: bool = True,
    enable_pagination: bool = True,
    page_size: int = 20,
    selection_mode: Optional[str] = None,  # 'single', 'multiple', None
    key: Optional[str] = None,
    fit_columns: bool = True,
    **kwargs
) -> Optional[pd.DataFrame]:
    """
    Render a dataframe with AgGrid if available, otherwise native Streamlit.
    
    Args:
        df: DataFrame to display
        title: Optional title above the table
        height: Table height in pixels
        enable_sorting: Allow column sorting
        enable_filtering: Allow column filtering
        enable_search: Show search box
        enable_pagination: Paginate results
        page_size: Rows per page
        selection_mode: Row selection mode
        key: Unique key for the component
        fit_columns: Auto-fit column widths
        
    Returns:
        Selected rows DataFrame if selection enabled, None otherwise
    """
    if df is None or df.empty:
        st.info("No data to display")
        return None
    
    if title:
        st.markdown(f"**{title}**")
    
    # Use AgGrid if available
    if AGGRID_AVAILABLE:
        return _render_aggrid(
            df, height, enable_sorting, enable_filtering, 
            enable_search, enable_pagination, page_size,
            selection_mode, key, fit_columns
        )
    else:
        # Fallback to native Streamlit
        return _render_native_dataframe(df, height, key)

def _render_aggrid(
    df: pd.DataFrame,
    height: int,
    enable_sorting: bool,
    enable_filtering: bool,
    enable_search: bool,
    enable_pagination: bool,
    page_size: int,
    selection_mode: Optional[str],
    key: Optional[str],
    fit_columns: bool
) -> Optional[pd.DataFrame]:
    """Render DataFrame using AgGrid"""
    try:
        # Build grid options
        gb = GridOptionsBuilder.from_dataframe(df)
        
        # Configure columns - make them flexible to fill width
        gb.configure_default_column(
            sortable=enable_sorting,
            filterable=enable_filtering,
            resizable=True,
            flex=1,  # Make columns flexible to fill available width
            minWidth=100,  # Minimum column width
        )
        
        # Pagination
        if enable_pagination:
            gb.configure_pagination(
                paginationAutoPageSize=False,
                paginationPageSize=page_size
            )
        
        # Selection
        if selection_mode:
            gb.configure_selection(
                selection_mode=selection_mode,
                use_checkbox=True
            )
        
        # Disable sidebar to save space (filtering still works via column headers)
        gb.configure_side_bar(filters_panel=False, columns_panel=False)
        
        # Build options
        grid_options = gb.build()
        
        # Force columns to fill grid width
        grid_options['domLayout'] = 'normal'
        grid_options['suppressHorizontalScroll'] = False
        
        # Dark theme custom CSS - comprehensive coverage
        custom_css = {
            # Root wrapper and body
            ".ag-root-wrapper": {
                "background-color": DARK_THEME['bg_card'] + " !important",
                "border-radius": "8px",
                "border": f"1px solid {DARK_THEME['border_subtle']}"
            },
            ".ag-body": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-body-viewport": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-body-horizontal-scroll-viewport": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-center-cols-viewport": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-center-cols-container": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            # Header
            ".ag-header": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
                "color": DARK_THEME['text_primary'],
            },
            ".ag-header-viewport": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
            },
            ".ag-header-cell": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
            },
            ".ag-header-cell-text": {
                "color": DARK_THEME['text_primary'] + " !important",
                "font-weight": "600"
            },
            # Rows
            ".ag-row": {
                "background-color": DARK_THEME['bg_card'] + " !important",
                "color": DARK_THEME['text_primary'],
            },
            ".ag-row-odd": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
            },
            ".ag-row-even": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-row-hover": {
                "background-color": DARK_THEME['bg_hover'] + " !important",
            },
            # Cells
            ".ag-cell": {
                "color": DARK_THEME['text_primary'] + " !important",
                "background-color": "transparent !important",
            },
            # Pagination and status bar
            ".ag-paging-panel": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
                "color": DARK_THEME['text_primary'] + " !important",
            },
            ".ag-status-bar": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
                "color": DARK_THEME['text_primary'] + " !important",
            },
            # Side bar (filters)
            ".ag-side-bar": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-tool-panel-wrapper": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            # Overlay (no rows)
            ".ag-overlay": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-overlay-no-rows-wrapper": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            # Scrollbar area
            ".ag-body-horizontal-scroll": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-body-vertical-scroll": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            # Input fields
            ".ag-text-field-input": {
                "background-color": DARK_THEME['bg_secondary'] + " !important",
                "color": DARK_THEME['text_primary'] + " !important",
            },
            # Menu and popup
            ".ag-menu": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
            ".ag-popup": {
                "background-color": DARK_THEME['bg_card'] + " !important",
            },
        }
        
        # Render grid
        response = AgGrid(
            df,
            gridOptions=grid_options,
            height=height,
            width='100%',
            theme='balham-dark',
            custom_css=custom_css,
            update_mode=GridUpdateMode.SELECTION_CHANGED if selection_mode else GridUpdateMode.NO_UPDATE,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            fit_columns_on_grid_load=fit_columns,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_ALL_COLUMNS_TO_VIEW,
            key=key,
            allow_unsafe_jscode=True
        )
        
        # Return selected rows if selection enabled
        if selection_mode and response.selected_rows is not None:
            return pd.DataFrame(response.selected_rows)
        
        return None
        
    except Exception as e:
        st.warning(f"AgGrid error, using fallback: {e}")
        return _render_native_dataframe(df, height, key)

def _render_native_dataframe(
    df: pd.DataFrame,
    height: int,
    key: Optional[str]
) -> None:
    """Fallback: render with native Streamlit dataframe"""
    st.dataframe(
        df,
        height=height,
        use_container_width=True,
        key=key
    )
    return None

# ==========================================
# 2. GAUGE CHARTS (ECharts with fallback)
# ==========================================

def render_gauge(
    value: float,
    title: str = "Score",
    min_value: float = 0,
    max_value: float = 100,
    thresholds: Optional[List[tuple]] = None,
    height: int = 250,
    key: Optional[str] = None
):
    """
    Render a gauge chart for scores/ratings.
    
    Args:
        value: Current value to display
        title: Gauge title
        min_value: Minimum scale value
        max_value: Maximum scale value
        thresholds: List of (value, color) tuples for color ranges
                   e.g., [(30, '#ef4444'), (70, '#f59e0b'), (100, '#10b981')]
        height: Chart height
        key: Unique key
    """
    if thresholds is None:
        thresholds = [
            (30, DARK_THEME['accent_danger']),    # 0-30: Red
            (70, DARK_THEME['accent_warning']),   # 30-70: Yellow
            (100, DARK_THEME['accent_success'])   # 70-100: Green
        ]
    
    if ECHARTS_AVAILABLE:
        _render_echarts_gauge(value, title, min_value, max_value, thresholds, height, key)
    else:
        _render_native_gauge(value, title, min_value, max_value)

def _render_echarts_gauge(
    value: float,
    title: str,
    min_value: float,
    max_value: float,
    thresholds: List[tuple],
    height: int,
    key: Optional[str]
):
    """Render gauge using ECharts"""
    try:
        # Build color axis from thresholds
        axis_line_colors = []
        prev = 0
        for threshold, color in thresholds:
            normalized = (threshold - min_value) / (max_value - min_value)
            axis_line_colors.append([normalized, color])
        
        option = {
            "series": [{
                "type": "gauge",
                "startAngle": 180,
                "endAngle": 0,
                "min": min_value,
                "max": max_value,
                "splitNumber": 5,
                "axisLine": {
                    "lineStyle": {
                        "width": 20,
                        "color": axis_line_colors
                    }
                },
                "pointer": {
                    "icon": "path://M12.8,0.7l12,40.1H0.7L12.8,0.7z",
                    "length": "60%",
                    "width": 8,
                    "offsetCenter": [0, "-10%"],
                    "itemStyle": {
                        "color": DARK_THEME['text_primary']
                    }
                },
                "axisTick": {
                    "length": 8,
                    "lineStyle": {
                        "color": DARK_THEME['text_secondary']
                    }
                },
                "splitLine": {
                    "length": 15,
                    "lineStyle": {
                        "color": DARK_THEME['text_secondary']
                    }
                },
                "axisLabel": {
                    "color": DARK_THEME['text_secondary'],
                    "fontSize": 12,
                    "distance": -50
                },
                "title": {
                    "offsetCenter": [0, "20%"],
                    "fontSize": 14,
                    "color": DARK_THEME['text_secondary']
                },
                "detail": {
                    "fontSize": 28,
                    "offsetCenter": [0, "50%"],
                    "valueAnimation": True,
                    "color": DARK_THEME['text_primary'],
                    "formatter": "{value}"
                },
                "data": [{
                    "value": round(value, 1),
                    "name": title
                }]
            }],
            "backgroundColor": "#1e2530"
        }
        
        st_echarts(option, height=f"{height}px", key=key)
        
    except Exception as e:
        st.warning(f"ECharts error, using fallback: {e}")
        _render_native_gauge(value, title, min_value, max_value)

def _render_native_gauge(
    value: float,
    title: str,
    min_value: float,
    max_value: float
):
    """Fallback: render gauge as metric with progress bar"""
    normalized = (value - min_value) / (max_value - min_value)
    
    # Determine color based on value
    if normalized < 0.3:
        delta_color = "inverse"
    elif normalized < 0.7:
        delta_color = "off"
    else:
        delta_color = "normal"
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(title, f"{value:.1f}", delta=None)
    with col2:
        st.progress(min(1.0, max(0.0, normalized)))

# ==========================================
# 3. RADAR CHARTS (ECharts)
# ==========================================

def render_radar_chart(
    data: Dict[str, float],
    title: str = "Analysis",
    max_value: float = 100,
    height: int = 350,
    key: Optional[str] = None
):
    """
    Render a radar/spider chart for multi-dimensional comparison.
    
    Args:
        data: Dict of {metric_name: value}
        title: Chart title
        max_value: Maximum value for each axis
        height: Chart height
        key: Unique key
    """
    if ECHARTS_AVAILABLE:
        _render_echarts_radar(data, title, max_value, height, key)
    else:
        _render_native_radar(data, title)

def _render_echarts_radar(
    data: Dict[str, float],
    title: str,
    max_value: float,
    height: int,
    key: Optional[str]
):
    """Render radar chart using ECharts"""
    try:
        indicators = [{"name": k, "max": max_value} for k in data.keys()]
        values = list(data.values())
        
        option = {
            "title": {
                "text": title,
                "left": "center",
                "textStyle": {"color": DARK_THEME['text_primary']}
            },
            "radar": {
                "indicator": indicators,
                "axisName": {"color": DARK_THEME['text_secondary']},
                "splitArea": {"areaStyle": {"color": ["transparent"]}},
                "axisLine": {"lineStyle": {"color": DARK_THEME['border_subtle']}},
                "splitLine": {"lineStyle": {"color": DARK_THEME['border_subtle']}}
            },
            "series": [{
                "type": "radar",
                "data": [{
                    "value": values,
                    "areaStyle": {"color": f"rgba(59, 130, 246, 0.3)"},
                    "lineStyle": {"color": DARK_THEME['accent_primary']},
                    "itemStyle": {"color": DARK_THEME['accent_primary']}
                }]
            }],
            "backgroundColor": "transparent"
        }
        
        st_echarts(option, height=f"{height}px", key=key)
        
    except Exception as e:
        st.warning(f"ECharts radar error: {e}")
        _render_native_radar(data, title)

def _render_native_radar(data: Dict[str, float], title: str):
    """Fallback: render as horizontal bar chart"""
    st.markdown(f"**{title}**")
    for metric, value in data.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.text(metric)
        with col2:
            st.progress(min(1.0, value / 100))

# ==========================================
# 4. PRICE CHARTS (Lightweight Charts)
# ==========================================

def render_price_chart(
    df: pd.DataFrame,
    chart_type: str = "candlestick",
    height: int = 400,
    show_volume: bool = True,
    title: Optional[str] = None,
    key: Optional[str] = None
):
    """
    Render TradingView-style price chart.
    
    Args:
        df: DataFrame with columns: Date, Open, High, Low, Close, Volume
        chart_type: 'candlestick', 'area', or 'line'
        height: Chart height
        show_volume: Show volume bars
        title: Optional title
        key: Unique key
    """
    if df is None or df.empty:
        st.info("No price data available")
        return
    
    if title:
        st.markdown(f"**{title}**")
    
    # Chart type selector
    chart_type = st.radio(
        "Chart Type",
        ["Candlestick", "Area", "Line"],
        horizontal=True,
        key=f"{key}_type" if key else None
    ).lower()
    
    if LIGHTWEIGHT_CHARTS_AVAILABLE:
        _render_lightweight_chart(df, chart_type, height, show_volume, key)
    else:
        _render_plotly_chart(df, chart_type, height, show_volume)

def _render_lightweight_chart(
    df: pd.DataFrame,
    chart_type: str,
    height: int,
    show_volume: bool,
    key: Optional[str]
):
    """Render using lightweight-charts"""
    try:
        # Prepare data
        df = df.copy()
        
        # Ensure datetime index
        if 'Date' in df.columns:
            df['time'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        elif df.index.name == 'Date' or isinstance(df.index, pd.DatetimeIndex):
            df['time'] = df.index.strftime('%Y-%m-%d')
        
        # Rename columns for lightweight-charts
        column_map = {
            'Open': 'open', 'High': 'high', 'Low': 'low', 
            'Close': 'close', 'Volume': 'volume'
        }
        df = df.rename(columns=column_map)
        
        # Create chart
        chart = StreamlitChart(height=height)
        
        if chart_type == 'candlestick':
            chart.candlestick_chart()
        elif chart_type == 'area':
            chart.area_chart()
        else:
            chart.line_chart()
        
        # Set data
        required_cols = ['time', 'open', 'high', 'low', 'close']
        if all(col in df.columns for col in required_cols):
            chart.set(df[required_cols + (['volume'] if show_volume and 'volume' in df.columns else [])])
        
        chart.load()
        
    except Exception as e:
        st.warning(f"Lightweight charts error, using Plotly: {e}")
        _render_plotly_chart(df, chart_type, height, show_volume)

def _render_plotly_chart(
    df: pd.DataFrame,
    chart_type: str,
    height: int,
    show_volume: bool
):
    """Fallback: render using Plotly"""
    try:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Prepare data
        if 'Date' not in df.columns and isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
        
        # Create figure
        if show_volume and 'Volume' in df.columns:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                               vertical_spacing=0.03, row_heights=[0.7, 0.3])
        else:
            fig = go.Figure()
        
        # Main chart
        if chart_type == 'candlestick':
            fig.add_trace(go.Candlestick(
                x=df['Date'] if 'Date' in df.columns else df.index,
                open=df['Open'], high=df['High'],
                low=df['Low'], close=df['Close'],
                name='Price'
            ), row=1 if show_volume and 'Volume' in df.columns else None, 
               col=1 if show_volume and 'Volume' in df.columns else None)
        elif chart_type == 'area':
            fig.add_trace(go.Scatter(
                x=df['Date'] if 'Date' in df.columns else df.index,
                y=df['Close'],
                fill='tozeroy',
                name='Price'
            ), row=1 if show_volume and 'Volume' in df.columns else None,
               col=1 if show_volume and 'Volume' in df.columns else None)
        else:
            fig.add_trace(go.Scatter(
                x=df['Date'] if 'Date' in df.columns else df.index,
                y=df['Close'],
                mode='lines',
                name='Price'
            ), row=1 if show_volume and 'Volume' in df.columns else None,
               col=1 if show_volume and 'Volume' in df.columns else None)
        
        # Volume bars
        if show_volume and 'Volume' in df.columns:
            fig.add_trace(go.Bar(
                x=df['Date'] if 'Date' in df.columns else df.index,
                y=df['Volume'],
                name='Volume',
                marker_color=DARK_THEME['accent_primary']
            ), row=2, col=1)
        
        # Dark theme styling
        fig.update_layout(
            template='plotly_dark',
            paper_bgcolor=DARK_THEME['bg_card'],
            plot_bgcolor=DARK_THEME['bg_card'],
            height=height,
            margin=dict(l=50, r=50, t=30, b=30),
            showlegend=False,
            xaxis_rangeslider_visible=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Chart rendering failed: {e}")

# ==========================================
# 5. DATA EXPLORER (PyGWalker)
# ==========================================

def render_data_explorer(
    df: pd.DataFrame,
    title: str = "Interactive Data Explorer",
    height: int = 600,
    key: Optional[str] = None
):
    """
    Render PyGWalker Tableau-like data explorer.
    
    Args:
        df: DataFrame to explore
        title: Section title
        height: Explorer height
        key: Unique key
    """
    with st.expander(f"📊 {title}", expanded=False):
        if PYGWALKER_AVAILABLE:
            _render_pygwalker(df, height, key)
        else:
            _render_native_explorer(df)

def _render_pygwalker(df: pd.DataFrame, height: int, key: Optional[str]):
    """Render using PyGWalker"""
    try:
        renderer = StreamlitRenderer(df, spec="./gw_config.json", debug=False)
        renderer.explorer(height=height)
    except Exception as e:
        st.warning(f"PyGWalker error: {e}")
        _render_native_explorer(df)

def _render_native_explorer(df: pd.DataFrame):
    """Fallback: basic data exploration"""
    st.info("Install `pygwalker` for interactive data exploration")
    
    # Basic stats
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Numeric Summary**")
        st.dataframe(df.describe(), use_container_width=True)
    with col2:
        st.markdown("**Data Types**")
        st.dataframe(pd.DataFrame(df.dtypes, columns=['Type']), use_container_width=True)

# ==========================================
# 6. LOADING ANIMATIONS (Lottie)
# ==========================================

def render_loading_animation(
    animation_type: str = "loading",
    height: int = 200,
    key: Optional[str] = None
):
    """
    Render Lottie loading animation.
    
    Args:
        animation_type: 'loading', 'success', 'error', 'chart'
        height: Animation height
        key: Unique key
    """
    # Professional minimal animations (from LottieFiles)
    animations = {
        "loading": "https://assets5.lottiefiles.com/packages/lf20_x62chJ.json",
        "success": "https://assets4.lottiefiles.com/packages/lf20_lk80fpsm.json",
        "error": "https://assets2.lottiefiles.com/packages/lf20_qpwbiyxf.json",
        "chart": "https://assets9.lottiefiles.com/packages/lf20_kxsd2ytq.json"
    }
    
    if LOTTIE_AVAILABLE:
        _render_lottie(animations.get(animation_type, animations["loading"]), height, key)
    else:
        _render_native_loading(animation_type)

def _render_lottie(url: str, height: int, key: Optional[str]):
    """Render Lottie animation"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            animation = response.json()
            st_lottie(animation, height=height, key=key)
        else:
            _render_native_loading("loading")
    except Exception as e:
        _render_native_loading("loading")

def _render_native_loading(animation_type: str):
    """Fallback: native Streamlit loading"""
    if animation_type == "loading":
        st.spinner("Loading...")
    elif animation_type == "success":
        st.success("Complete!")
    elif animation_type == "error":
        st.error("Error occurred")
    else:
        st.info("Processing...")

# ==========================================
# 7. STYLED HEADERS (Extras)
# ==========================================

def render_styled_header(
    title: str,
    description: Optional[str] = None,
    color: str = "blue"
):
    """
    Render a styled section header.
    
    Args:
        title: Header title
        description: Optional description
        color: 'blue', 'green', 'orange', 'red', 'violet'
    """
    if EXTRAS_AVAILABLE:
        try:
            colored_header(
                label=title,
                description=description or "",
                color_name=f"{color}-70"
            )
        except Exception:
            _render_native_header(title, description)
    else:
        _render_native_header(title, description)

def _render_native_header(title: str, description: Optional[str]):
    """Fallback: native header"""
    st.markdown(f"## {title}")
    if description:
        st.caption(description)

# ==========================================
# 8. METRIC CARDS (Extras)
# ==========================================

def style_metrics():
    """Apply enhanced styling to st.metric cards"""
    if EXTRAS_AVAILABLE:
        try:
            style_metric_cards(
                background_color=DARK_THEME['bg_card'],
                border_left_color=DARK_THEME['accent_primary'],
                border_color=DARK_THEME['border_subtle'],
                box_shadow=True
            )
        except Exception:
            pass  # Silent fail, metrics still work

# ==========================================
# 9. COLLAPSIBLE SECTIONS (Extras)
# ==========================================

def render_toggle(
    label: str,
    content: str,
    key: Optional[str] = None
):
    """
    Render a collapsible toggle section.
    
    Args:
        label: Toggle label
        content: Content to show when expanded
        key: Unique key
    """
    if EXTRAS_AVAILABLE:
        try:
            stoggle(label, content)
        except Exception:
            _render_native_toggle(label, content)
    else:
        _render_native_toggle(label, content)

def _render_native_toggle(label: str, content: str):
    """Fallback: native expander"""
    with st.expander(label):
        st.markdown(content)


# ==========================================
# INITIALIZATION
# ==========================================

def init_ui_components():
    """Initialize UI components - call at app start"""
    # Apply metric card styling
    style_metrics()
    
    # Log library status (debug mode)
    status = get_library_status()
    available = sum(1 for v in status.values() if v)
    total = len(status)
    
    # Only log, don't show to user
    import logging
    logging.getLogger("UIComponents").info(f"UI Libraries: {available}/{total} available")


if __name__ == "__main__":
    # Test mode
    st.set_page_config(page_title="UI Components Test", layout="wide")
    st.title("UI Components Test")
    
    show_library_status()
    
    # Test gauge
    st.header("Gauge Test")
    render_gauge(75, "Investment Score")
    
    # Test table
    st.header("Table Test")
    test_df = pd.DataFrame({
        'Metric': ['Revenue', 'Net Income', 'EPS'],
        '2023': [100, 20, 2.5],
        '2024': [120, 25, 3.0]
    })
    smart_dataframe(test_df, title="Financial Metrics")

