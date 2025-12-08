@echo off
echo ================================================
echo TESTING INVESTMENT SUMMARY + BLUE THEME
echo ================================================
echo.
echo New Features:
echo  1. Blue Corporate Theme (professional look)
echo  2. Investment Summary Tab (one-page decision sheet)
echo.
echo Test with these companies:
echo  - AAPL (high profitability)
echo  - TSLA (high growth/valuation)
echo  - JPM (financial sector)
echo  - F (high leverage)
echo  - XOM (energy sector)
echo.
echo Navigate to "Investment Summary" tab after extracting!
echo.
echo Press Ctrl+C to stop when done
echo.
pause
streamlit run usa_app.py


