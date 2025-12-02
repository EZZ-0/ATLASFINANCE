@echo off
REM ========================================
REM CODEBASE EXPORT - QUICK LAUNCHER
REM ========================================
REM Generates sanitized codebase for auditors

echo ========================================
echo   CODEBASE EXPORT FOR AUDITORS
echo ========================================
echo.
echo This will create a complete copy of the codebase
echo with all API keys and sensitive data removed.
echo.
echo Output: ATLAS_ENGINE_CODEBASE_EXPORT_[timestamp].txt
echo.
pause

python export_codebase.py

echo.
echo ========================================
echo Export complete! Check the current folder.
echo ========================================
pause


