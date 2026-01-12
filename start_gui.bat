@echo off
echo ========================================
echo Video Analyzer GUI
echo ========================================
echo.
echo Installing dependencies...
pip install -q -r requirements.txt
echo.
echo Starting application...
python video_analyzer_gui.py
pause