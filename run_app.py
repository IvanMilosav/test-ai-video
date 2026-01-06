#!/usr/bin/env python3
"""
Run the Script-to-Clip application.
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Script-to-Clip API...")
    print("Open http://localhost:8000/app in your browser")
    print()
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
