#!/bin/bash

# Script-to-Clip Application Starter
# Starts the FastAPI backend and opens the frontend in the browser

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install dependencies if needed
pip install -q -r requirements.txt

# Create necessary directories
mkdir -p uploads generated_images

echo "Starting Script-to-Clip API..."
echo "Open http://localhost:8000/app in your browser"
echo ""

# Open browser after a short delay (in background)
(sleep 2 && open "http://localhost:8000/app" 2>/dev/null || xdg-open "http://localhost:8000/app" 2>/dev/null) &

# Start the server
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
