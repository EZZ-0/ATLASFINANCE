@echo off
echo ========================================
echo   LIVE DCF MODELING - FEATURE TEST
echo ========================================
echo.
echo NEW FEATURES TO TEST:
echo  1. Live Slider Interface (10 parameters)
echo  2. Quick Preview (instant estimates)
echo  3. Full DCF Calculation
echo  4. Save Custom Scenarios
echo  5. Load Saved Scenarios
echo  6. Compare to Presets
echo  7. Scenario Library Management
echo.
echo TEST FLOW:
echo  Step 1: Extract a ticker (e.g., AAPL)
echo  Step 2: Go to Model tab
echo  Step 3: Click "Live Scenario Builder"
echo  Step 4: Adjust sliders
echo  Step 5: Run Full DCF
echo  Step 6: Save scenario
echo  Step 7: Load scenario
echo.
echo ========================================
echo.
echo Starting app...
echo.
streamlit run usa_app.py


