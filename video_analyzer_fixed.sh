#!/bin/bash
# Video Analyzer GUI Launcher - Fixed Version
# This version includes better error handling and logging

LOG_FILE="/tmp/video_analyzer.log"

# Start logging
{
    echo "========================================"
    echo "Video Analyzer Startup - $(date)"
    echo "========================================"

    # Get the directory where this script is located
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo "Script directory: $SCRIPT_DIR"

    # Change to the script directory
    cd "$SCRIPT_DIR" || {
        echo "ERROR: Cannot change to script directory"
        exit 1
    }

    echo "Working directory: $(pwd)"
    echo ""

    # Check for virtual environment and use it
    if [ -d "$SCRIPT_DIR/venv" ]; then
        PYTHON_CMD="$SCRIPT_DIR/venv/bin/python3"
        echo "✓ Using virtual environment"
        echo "  Python: $PYTHON_CMD"
        echo "  Version: $("$PYTHON_CMD" --version)"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD=python3
        echo "⚠ Using system Python (no venv found)"
        echo "  Python found: $(which python3)"
        echo "  Version: $(python3 --version)"
    elif command -v python &> /dev/null; then
        PYTHON_CMD=python
        echo "⚠ Using system Python (no venv found)"
        echo "  Python found: $(which python)"
        echo "  Version: $(python --version)"
    else
        echo "✗ ERROR: Python not found"
        if command -v zenity &> /dev/null; then
            zenity --error --text="Python 3 is not installed.\nPlease install Python 3 to run Video Analyzer." --width=300
        fi
        exit 1
    fi
    echo ""

    # Check for required files
    echo "Checking required files..."
    if [ ! -f "video_analyzer_gui.py" ]; then
        echo "✗ ERROR: video_analyzer_gui.py not found"
        exit 1
    fi
    echo "✓ video_analyzer_gui.py found"

    if [ ! -f ".env" ]; then
        echo "⚠ WARNING: .env file not found"
    else
        echo "✓ .env file found"
    fi

    if [ ! -f "config.py" ]; then
        echo "✗ ERROR: config.py not found"
        exit 1
    fi
    echo "✓ config.py found"
    echo ""

    # Check for required Python packages
    echo "Checking Python packages..."
    "$PYTHON_CMD" -c "import tkinter" 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ tkinter available"
    else
        echo "✗ ERROR: tkinter not available"
        if command -v zenity &> /dev/null; then
            zenity --error --text="Python tkinter is not installed.\nPlease install it: sudo apt-get install python3-tk" --width=400
        fi
        exit 1
    fi
    echo ""

    # Launch the GUI
    echo "Launching Video Analyzer GUI..."
    echo "========================================"
    echo ""

    "$PYTHON_CMD" video_analyzer_gui.py 2>&1

    EXIT_CODE=$?
    echo ""
    echo "========================================"
    echo "Exit code: $EXIT_CODE"

    if [ $EXIT_CODE -ne 0 ]; then
        echo "✗ Application exited with errors"
        if command -v zenity &> /dev/null; then
            zenity --error --text="Video Analyzer failed to start.\n\nCheck log file:\n$LOG_FILE" --width=400
        fi
    else
        echo "✓ Application closed normally"
    fi

} 2>&1 | tee "$LOG_FILE"

exit $EXIT_CODE
