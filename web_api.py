#!/usr/bin/env python3
"""
Video Analyzer Web API
Simplified API for web-based video analysis deployment
"""

import os
import tempfile
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from iterative_analyzer import IterativeClipAnalyzer
import glob

# Create FastAPI app
app = FastAPI(title="Video Analyzer API", version="1.0.0")

# CORS - allow all origins for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("temp_uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the web application"""
    return FileResponse("public/index.html")


@app.post("/api/analyze-video")
async def analyze_video(
    video: UploadFile = File(...)
):
    """
    Analyze a video file and return the results
    Uses API key from .env file

    Args:
        video: The video file to analyze
    """
    temp_video_path = None

    try:
        # Check if API key is configured in .env
        from config import Config
        if not Config.GOOGLE_API_KEY:
            raise HTTPException(
                status_code=400,
                detail="API key not configured. Please create a .env file with GOOGLE_API_KEY=your_key_here"
            )

        # Validate file size (20MB limit)
        file_size = 0
        temp_video_path = os.path.join("temp_uploads", f"temp_{datetime.now().timestamp()}_{video.filename}")

        with open(temp_video_path, "wb") as f:
            while chunk := await video.read(1024 * 1024):  # Read 1MB at a time
                file_size += len(chunk)
                if file_size > 20 * 1024 * 1024:  # 20MB limit
                    raise HTTPException(status_code=413, detail="Video file too large. Maximum size is 20MB.")
                f.write(chunk)

        # Create analyzer (uses Config.GOOGLE_API_KEY from .env)
        analyzer = IterativeClipAnalyzer(
            model='pro',
            ontology_path='master_clip_ontology.pkl'
        )

        # Process video
        result = analyzer.process_video(temp_video_path, None)

        return JSONResponse({
            "success": True,
            "output": result.get('output', 'Analysis complete'),
            "output_file": result.get('output', None),
            "message": "Video analyzed successfully"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if temp_video_path and os.path.exists(temp_video_path):
            try:
                os.remove(temp_video_path)
            except:
                pass


@app.get("/api/data/master-ontology")
async def get_master_ontology():
    """Get the master ontology file contents"""
    file_path = "master_clip_ontology.txt"

    if not os.path.exists(file_path):
        return JSONResponse({
            "content": "No master ontology data yet. Analyze some videos first!"
        })

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return JSONResponse({"content": content})


@app.get("/api/data/script-clip-brain")
async def get_script_clip_brain():
    """Get the script-clip brain file contents"""
    file_path = "script_clip_brain.txt"

    if not os.path.exists(file_path):
        return JSONResponse({
            "content": "No script-clip brain data yet. Analyze some videos first!"
        })

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return JSONResponse({"content": content})


@app.get("/api/data/history")
async def get_analysis_history():
    """Get list of all analysis files"""
    pattern = "*_ontology_*.txt"
    files = glob.glob(pattern)

    # Filter out master ontology
    files = [f for f in files if not f.startswith("master_")]

    # Sort by modification time (newest first)
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # Format file information
    file_list = []
    for file_path in files:
        stat = os.stat(file_path)
        file_list.append({
            "name": os.path.basename(file_path),
            "path": file_path,
            "size": f"{stat.st_size / 1024:.1f} KB",
            "date": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        })

    return JSONResponse({"files": file_list})


@app.get("/api/data/file")
async def get_file_content(path: str):
    """Get contents of a specific analysis file"""
    # Security: ensure path doesn't escape current directory
    if ".." in path or path.startswith("/"):
        raise HTTPException(status_code=403, detail="Invalid file path")

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    return JSONResponse({"content": content})


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    print("Starting Video Analyzer Web App...")
    print("Open http://localhost:8000 in your browser")
    uvicorn.run(app, host="0.0.0.0", port=8000)
