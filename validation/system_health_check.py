"""
SYSTEM HEALTH CHECK
===================
Validates all modules after 14 milestones.

Tests:
1. Import checks - All modules import without errors
2. Dependency checks - No circular imports
3. API checks - Key functions callable
4. Data checks - Sample extraction works

Author: ATLAS Architect
Date: 2025-12-08
"""

import sys
import os
import traceback
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RESULTS = {
    'passed': [],
    'failed': [],
    'warnings': []
}

def test(name):
    """Decorator to run and record test results."""
    def decorator(func):
        def wrapper():
            try:
                result = func()
                if result:
                    RESULTS['passed'].append(name)
                    print(f"  ✅ {name}")
                else:
                    RESULTS['failed'].append(name)
                    print(f"  ❌ {name}")
            except Exception as e:
                RESULTS['failed'].append(f"{name}: {str(e)[:50]}")
                print(f"  ❌ {name}: {str(e)[:50]}")
        return wrapper
    return decorator


print("=" * 60)
print("SYSTEM HEALTH CHECK - Post 14 Milestones")
print(f"Time: {datetime.now()}")
print("=" * 60)

# ============================================
# 1. CORE MODULE IMPORTS
# ============================================
print("\n[1] CORE MODULE IMPORTS")

@test("usa_backend")
def test_usa_backend():
    from usa_backend import USAFinancialExtractor
    return True

@test("validation_engine")
def test_validation_engine():
    from validation_engine import DataValidator
    return True

@test("app_css")
def test_app_css():
    from app_css import inject_all_css
    return True

@test("app_landing")
def test_app_landing():
    from app_landing import render_landing_page
    return True

@test("app_themes")
def test_app_themes():
    from app_themes import inject_theme_css, get_current_theme
    return True

test_usa_backend()
test_validation_engine()
test_app_css()
test_app_landing()
test_app_themes()

# ============================================
# 2. MILESTONE MODULE IMPORTS
# ============================================
print("\n[2] MILESTONE MODULES")

@test("M001: benchmark_validator")
def test_m001():
    from validation.benchmark_validator import BenchmarkValidator
    return True

@test("M002: earnings_revisions")
def test_m002():
    from earnings_revisions import EarningsRevisionTracker
    return True

@test("M003: insider_transactions")
def test_m003():
    from insider_transactions import get_insider_summary
    return True

@test("M004: institutional_ownership")
def test_m004():
    from institutional_ownership import get_ownership_summary
    return True

@test("M005: pdf_export_enhanced")
def test_m005():
    from pdf_export_enhanced import generate_enhanced_ic_memo
    return True

@test("M006: config/themes")
def test_m006():
    from config.themes import THEMES, get_theme
    return True

@test("M007: utils/ticker_cache")
def test_m007():
    from utils.ticker_cache import get_ticker, get_ticker_info
    return True

@test("M008: flip_cards")
def test_m008():
    from flip_cards import render_flip_card, METRICS
    return len(METRICS) >= 20

@test("M012: utils/bank_metrics")
def test_m012():
    from utils.bank_metrics import is_bank, BANK_TICKERS
    return len(BANK_TICKERS) > 0

@test("M014: components/draggable_grid")
def test_m014():
    from components.draggable_grid import GridConfig, render_reorder_controls
    return True

@test("M015: components/mobile_responsive")
def test_m015():
    from components.mobile_responsive import inject_responsive_css
    return True

test_m001()
test_m002()
test_m003()
test_m004()
test_m005()
test_m006()
test_m007()
test_m008()
test_m012()
test_m014()
test_m015()

# ============================================
# 3. DATA SOURCE IMPORTS
# ============================================
print("\n[3] DATA SOURCES")

@test("data_sources/fred_api")
def test_fred():
    from data_sources.fred_api import get_risk_free_rate, FREDClient
    return True

@test("data_sources/damodaran_data")
def test_damodaran():
    from data_sources.damodaran_data import get_industry_benchmark, DamodaranData
    return True

@test("data_sources/fmp_earnings")
def test_fmp():
    from data_sources.fmp_earnings import FMPEarningsClient
    return True

test_fred()
test_damodaran()
test_fmp()

# ============================================
# 4. TAB IMPORTS
# ============================================
print("\n[4] TAB MODULES")

@test("dashboard_tab")
def test_dashboard():
    from dashboard_tab import render_dashboard_tab
    return True

@test("analysis_tab")
def test_analysis():
    from analysis_tab import render_analysis_tab
    return True

@test("investment_summary")
def test_summary():
    from investment_summary import render_investment_summary_tab
    return True

test_dashboard()
test_analysis()
test_summary()

# ============================================
# 5. QUICK FUNCTIONALITY TEST
# ============================================
print("\n[5] FUNCTIONALITY TESTS")

@test("yfinance extraction")
def test_yfinance():
    import yfinance as yf
    stock = yf.Ticker("AAPL")
    info = stock.info
    return 'currentPrice' in info or 'regularMarketPrice' in info

@test("flip_cards color logic")
def test_flip_colors():
    from flip_cards import get_metric_color
    green = get_metric_color(25, "ROE")  # High ROE = green
    red = get_metric_color(5, "ROE")     # Low ROE = red
    return green == "#10b981" and red == "#ef4444"

@test("bank detection")
def test_bank_detection():
    from utils.bank_metrics import is_bank
    return is_bank("JPM") == True and is_bank("AAPL") == False

test_yfinance()
test_flip_colors()
test_bank_detection()

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

total = len(RESULTS['passed']) + len(RESULTS['failed'])
passed = len(RESULTS['passed'])
failed = len(RESULTS['failed'])

print(f"\nPassed: {passed}/{total}")
print(f"Failed: {failed}/{total}")

if RESULTS['failed']:
    print("\n❌ FAILED TESTS:")
    for f in RESULTS['failed']:
        print(f"   - {f}")

if RESULTS['warnings']:
    print("\n⚠️ WARNINGS:")
    for w in RESULTS['warnings']:
        print(f"   - {w}")

if failed == 0:
    print("\n✅ SYSTEM HEALTH: ALL CHECKS PASSED")
else:
    print(f"\n⚠️ SYSTEM HEALTH: {failed} ISSUES FOUND")

print("=" * 60)

# Write report
report = f"""# System Health Check Report
Generated: {datetime.now()}

## Summary
- **Total Tests:** {total}
- **Passed:** {passed}
- **Failed:** {failed}

## Passed Tests
{chr(10).join(['- ' + p for p in RESULTS['passed']])}

## Failed Tests
{chr(10).join(['- ' + f for f in RESULTS['failed']]) if RESULTS['failed'] else 'None'}

## Conclusion
{'✅ All systems operational' if failed == 0 else f'⚠️ {failed} issues need attention'}
"""

with open('validation/system_health_report.md', 'w') as f:
    f.write(report)

print("\nReport saved: validation/system_health_report.md")

