@echo off
cd /d "%~dp0"
echo Starting local web server...
echo.
echo Opening dashboard at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
timeout /t 2
start http://localhost:8000/docs/dashboard.html
python -m http.server 8000
