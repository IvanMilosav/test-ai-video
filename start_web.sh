#!/bin/bash
# Start Video Analyzer Web Application
# For macOS/Linux

echo ""
echo "========================================"
echo "  VIDEO ANALYZER - Web Server"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d .venv_web ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv_web
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment!"
        echo "Make sure Python 3 is installed."
        read -p "Press Enter to exit..."
        exit 1
    fi
fi

# Activate virtual environment
source .venv_web/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment!"
    read -p "Press Enter to exit..."
    exit 1
fi

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements_web.txt
if [ $? -ne 0 ]; then
    echo "WARNING: Some dependencies may not have installed correctly."
fi

# Start web server
echo ""
echo "Starting web server..."
echo ""
echo "========================================"
echo " Server will start at:"
echo " http://localhost:8000"
echo ""
echo " Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python web_api.py

deactivate
