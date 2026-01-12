#!/bin/bash
echo "========================================"
echo "Video Analyzer GUI"
echo "========================================"
echo ""
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo ""
echo "Starting application..."
python3 video_analyzer_gui.py