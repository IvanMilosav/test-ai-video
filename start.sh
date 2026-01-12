#!/bin/sh
# Startup script for Railway deployment
# Uses PORT environment variable if provided, otherwise defaults to 8000

PORT=${PORT:-8000}
exec uvicorn web_api:app --host 0.0.0.0 --port $PORT
