@echo off
echo ====================================
echo   PROJECT CLEANUP SCRIPT
echo ====================================
echo.

echo Creating folder structure...
if not exist "docs" mkdir docs
if not exist "docs\reports" mkdir docs\reports
if not exist "docs\ui_research" mkdir docs\ui_research
if not exist "docs\guides" mkdir docs\guides
if not exist "docs\archive" mkdir docs\archive
if not exist "tests\archive" mkdir tests\archive

echo.
echo Moving REPORT files to docs\reports\...
move "FULL_TEST_REPORT.html" "docs\reports\" 2>nul
move "COMPREHENSIVE_AUDIT_REPORT.md" "docs\reports\" 2>nul
move "EXECUTIVE_SUMMARY.md" "docs\reports\" 2>nul
move "FINAL_RESOLUTION_REPORT.md" "docs\reports\" 2>nul
move "CRASH_FIX_REPORT.md" "docs\reports\" 2>nul
move "SESSION_STATUS_COMPLETE.md" "docs\reports\" 2>nul
move "IMPLEMENTATION_STATUS_AI.md" "docs\reports\" 2>nul
move "TEST_EXECUTION_SUMMARY.md" "docs\reports\" 2>nul
move "AUDIT_REPORT_ANALYSIS_COMPLETE.md" "docs\reports\" 2>nul
move "SECOND_AUDIT_ANALYSIS_COMPLETE.md" "docs\reports\" 2>nul
move "100_PERCENT_COMPLETE_REPORT.md" "docs\reports\" 2>nul
move "HEALTH_CHECK_REPORT.md" "docs\reports\" 2>nul
move "CRASH_RECOVERY_REPORT.md" "docs\reports\" 2>nul
move "TEST_AUDIT_BULLETPROOF.md" "docs\reports\" 2>nul

echo.
echo Moving UI RESEARCH files to docs\ui_research\...
move "UI_ENHANCEMENT_RESEARCH_REPORT.md" "docs\ui_research\" 2>nul
move "UI_QUICK_START_DEMO.md" "docs\ui_research\" 2>nul
move "UI_ENHANCEMENT_EXECUTIVE_SUMMARY.md" "docs\ui_research\" 2>nul
move "UI_DESIGN_WORKFLOW_GUIDE.md" "docs\ui_research\" 2>nul
move "UI_COMPETITIVE_RESEARCH.md" "docs\ui_research\" 2>nul
move "UI_ENHANCEMENT_ROADMAP.md" "docs\ui_research\" 2>nul
move "UI_FIXES_COMPLETE.md" "docs\ui_research\" 2>nul

echo.
echo Moving GUIDE files to docs\guides\...
move "AI_SETUP_GUIDE.md" "docs\guides\" 2>nul
move "QUICK_START.md" "docs\guides\" 2>nul
move "SETUP_USA.md" "docs\guides\" 2>nul
move "USA_README.md" "docs\guides\" 2>nul

echo.
echo Moving ARCHIVE files to docs\archive\...
move "PHASE_*_*.md" "docs\archive\" 2>nul
move "BACKUP_*.md" "docs\archive\" 2>nul
move "PROJECT_BACKUP_*.md" "docs\archive\" 2>nul
move "CONVERSATION_LOG_*.md" "docs\archive\" 2>nul
move "FINAL_SESSION_REPORT.md" "docs\archive\" 2>nul
move "SESSION_COMPLETE_SUMMARY.md" "docs\archive\" 2>nul
move "CONSOLIDATED_STATUS_AND_PLAN.md" "docs\archive\" 2>nul
move "PATH_TO_100_PERCENT.md" "docs\archive\" 2>nul
move "INTEGRATED_ROADMAP_FINAL.md" "docs\archive\" 2>nul
move "ACTION_REQUIRED_README.md" "docs\archive\" 2>nul
move "README_*.md" "docs\archive\" 2>nul
move "README_*.txt" "docs\archive\" 2>nul
move "*_COMPLETE.md" "docs\archive\" 2>nul
move "*_COMPLETE_REPORT.md" "docs\archive\" 2>nul
move "*_FIXES_COMPLETE.md" "docs\archive\" 2>nul
move "*_FIX*.md" "docs\archive\" 2>nul
move "IMPLEMENTATION_PLAN_*.md" "docs\archive\" 2>nul
move "REQUIREMENTS_*.md" "docs\archive\" 2>nul
move "REFACTORING_*.md" "docs\archive\" 2>nul
move "ISSUES_FIXED_REPORT.md" "docs\archive\" 2>nul
move "CRITICAL_FIXES_COMPLETE.md" "docs\archive\" 2>nul
move "VALIDATION_FIXES_COMPLETE.md" "docs\archive\" 2>nul
move "BUG_FIX_*.md" "docs\archive\" 2>nul
move "GOVERNANCE_BUG_FIXES_COMPLETE.md" "docs\archive\" 2>nul
move "TAB_ARCHITECTURE_AUDIT.md" "docs\archive\" 2>nul
move "CURSORIGNORE_RISK_ASSESSMENT.md" "docs\archive\" 2>nul
move "CIK_DEBUG_FIX.md" "docs\archive\" 2>nul
move "SEC_EDGAR_FINAL_STATUS.md" "docs\archive\" 2>nul
move "EXECUTIVE_SUMMARY_FIX.md" "docs\archive\" 2>nul
move "PEER_COMPARISON_FIX*.md" "docs\archive\" 2>nul
move "REVERSE_DCF_*.md" "docs\archive\" 2>nul
move "IR_LINK_FIX_COMPLETE.md" "docs\archive\" 2>nul
move "NEWS_TIMEZONE_FIX_REPORT.md" "docs\archive\" 2>nul
move "QUICK_FIX_*.md" "docs\archive\" 2>nul
move "HYBRID_OPTION_COMPLETE.md" "docs\archive\" 2>nul
move "CLEANUP_COMPLETE.md" "docs\archive\" 2>nul

echo.
echo Moving OLD TEST files to tests\archive\...
move "test_quick_validation.py" "tests\archive\" 2>nul
move "test_quick_day2.py" "tests\archive\" 2>nul
move "test_final_simple.py" "tests\archive\" 2>nul
move "test_day2_validation.py" "tests\archive\" 2>nul
move "golden_standard_test.py" "tests\archive\" 2>nul
move "diagnostic_test.py" "tests\archive\" 2>nul
move "diagnose_issue.py" "tests\archive\" 2>nul
move "validation_test_*.py" "tests\archive\" 2>nul
move "test_forensic_shield.py" "tests\archive\" 2>nul
move "test_reverse_dcf*.py" "tests\archive\" 2>nul
move "test_yfinance_structure.py" "tests\archive\" 2>nul
move "validation_master_runner.py" "tests\archive\" 2>nul
move "test_report_*.json" "tests\archive\" 2>nul
move "test_report_*.html" "tests\archive\" 2>nul

echo.
echo ====================================
echo   CLEANUP COMPLETE!
echo ====================================
echo.
echo Root folder now contains only:
echo   - Core app files (usa_app.py, usa_backend.py, financial_ai.py)
echo   - Current test files (test_all_17_companies.py, test_ai_validation.py)
echo   - Config files (requirements.txt, .env)
echo   - Batch scripts (run_app.bat, restart_app.bat)
echo   - README.md
echo.
echo All documentation moved to /docs/
echo All old tests moved to /tests/archive/
echo.
pause


