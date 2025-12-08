"""
ATLAS Financial Intelligence - Tab Modules
==========================================
Modular tab components for the main application.
Each tab is self-contained with its own render function.
"""

from tabs.tab_data import render_data_tab
from tabs.tab_valuation import render_valuation_tab
from tabs.tab_risk import render_risk_tab
from tabs.tab_market import render_market_tab
from tabs.tab_news import render_news_tab

__all__ = [
    'render_data_tab',
    'render_valuation_tab',
    'render_risk_tab',
    'render_market_tab',
    'render_news_tab',
]
