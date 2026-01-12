@echo off
REM Start Video Analyzer Web Application
REM For Windows

title Video Analyzer Web Server

echo.
echo ========================================
echo   VIDEO ANALYZER - Web Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist .venv_web (
    echo Creating virtual environment...
    python -m venv .venv_web
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment!
        echo Make sure Python is installed.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv_web\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)

REM Install/update dependencies
echo Checking dependencies...
pip install -q -r requirements_web.txt
if errorlevel 1 (
    echo WARNING: Some dependencies may not have installed correctly.
)

REM Start web server
echo.
echo Starting web server...
echo.
echo ========================================
echo  Server will start at:
echo  http://localhost:8000
echo.
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

python web_api.py

deactivate
