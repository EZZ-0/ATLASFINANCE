@echo off
echo ========================================
echo   CREATING BACKUP
echo ========================================
echo.

set BACKUP_NAME=Saudi_Earnings_Engine_BACKUP_%DATE:~-4%%DATE:~-10,2%%DATE:~-7,2%_%TIME:~0,2%%TIME:~3,2%
set BACKUP_NAME=%BACKUP_NAME: =0%

echo Backup Name: %BACKUP_NAME%
echo.

echo Creating backup folder...
cd ..
mkdir "%BACKUP_NAME%"

echo Copying files...
xcopy "Saudi_Earnings_Engine\*" "%BACKUP_NAME%\" /E /I /H /Y /EXCLUDE:Saudi_Earnings_Engine\backup_exclude.txt

echo.
echo ========================================
echo   BACKUP COMPLETE!
echo ========================================
echo.
echo Location: ..\%BACKUP_NAME%\
echo.
echo Files backed up:
echo   - All Python files
echo   - All configuration files
echo   - All documentation
echo   - All test files
echo.
echo Excluded:
echo   - __pycache__
echo   - *.pyc
echo   - build/
echo   - dist/
echo.
pause


