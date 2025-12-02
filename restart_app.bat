@echo off
echo ========================================
echo  USA EARNINGS ENGINE - CACHE CLEAR
echo ========================================
echo.
echo Clearing Python cache...
if exist __pycache__ rmdir /s /q __pycache__
if exist .streamlit\cache rmdir /s /q .streamlit\cache
echo.
echo Clearing Streamlit cache...
python -m streamlit cache clear
echo.
echo ========================================
echo  Starting USA Earnings Engine v2.1
echo ========================================
echo.
echo Features:
echo  - Multi-document support (10-K, 10-Q, S-1)
echo  - Fama-French 3-Factor quant analysis
echo  - Historical pricing (back to 1990)
echo  - 3-Scenario DCF valuation
echo  - Fixed: Adaptive number formatting
echo  - Fixed: Proper table layouts
echo  - Fixed: CSV export formatting
echo.
python -m streamlit run usa_app.py

