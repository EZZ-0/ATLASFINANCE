@echo off
REM ========================================
REM ATLAS FINANCIAL INTELLIGENCE - LAUNCHER
REM ========================================
REM Quick launcher for the Atlas Engine
REM No setup required - just double-click!

echo ========================================
echo    ATLAS FINANCIAL INTELLIGENCE
echo    Professional Financial Analysis Engine
echo ========================================
echo.
echo Starting the engine...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo Please create .env file with your API keys.
    echo Use .env.template as a reference.
    echo.
    pause
    exit /b 1
)

REM Launch Streamlit app
echo Launching Atlas Financial Intelligence...
echo.
echo Press Ctrl+C to stop the app
echo Browser will open automatically at http://localhost:8501
echo.

streamlit run usa_app.py

pause
