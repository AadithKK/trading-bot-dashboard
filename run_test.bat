@echo off
cd /d "%~dp0"
echo Running test_trading_cycle.py...
echo.
python test_trading_cycle.py
echo.
echo.
echo ====================================
echo Test completed. Check output above.
echo Press any key to close...
echo ====================================
pause
