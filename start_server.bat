@echo off
echo ============================================================
echo       BOUNCER BACKEND - PERSON INTELLIGENCE API
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo Checking Python installation...
python --version

echo.
echo Installing/checking dependencies...
pip install flask flask-cors requests python-dotenv google-generativeai beautifulsoup4 anthropic

echo.
echo Starting Bouncer Backend Server...
echo Server will be available at: http://localhost:5001
echo Press Ctrl+C to stop the server
echo.

python start_server.py

pause 