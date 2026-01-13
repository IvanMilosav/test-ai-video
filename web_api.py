#!/usr/bin/env python3
"""
Video Analyzer Web API
Simplified API for web-based video analysis deployment
"""

import os
import sys
import tempfile
from datetime import datetime
from io import StringIO
from contextlib import redirect_stdout
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from iterative_analyzer import IterativeClipAnalyzer
import glob
import asyncio
import json
import subprocess

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


def compress_video(input_path: str, output_path: str, target_size_mb: float = 18) -> bool:
    """
    Fast video compression using ffmpeg with optimized settings for speed

    Args:
        input_path: Path to input video
        output_path: Path to save compressed video
        target_size_mb: Target size in MB (default 18MB to leave buffer under 20MB)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get video duration and current size
        probe_cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration,size', '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=10)
        lines = result.stdout.strip().split('\n')
        duration = float(lines[0])
        current_size_mb = float(lines[1]) / (1024 * 1024)

        # Calculate target bitrate (in kbps)
        target_size_bits = target_size_mb * 8 * 1024 * 1024
        target_bitrate = int((target_size_bits / duration) * 0.90)  # 90% for video, rest for audio

        print(f"Compressing: {current_size_mb:.1f}MB -> {target_size_mb}MB (duration: {duration:.1f}s, bitrate: {target_bitrate}k)")

        # Fast compression with ultrafast preset
        compress_cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',  # H.264 codec
            '-preset', 'ultrafast',  # FAST encoding (was 'medium')
            '-crf', '28',  # Constant rate factor (quality, 23 is default, 28 is lower quality but faster)
            '-b:v', f'{target_bitrate}k',  # Target video bitrate
            '-maxrate', f'{target_bitrate}k',
            '-bufsize', f'{target_bitrate}k',
            '-vf', 'scale=\'min(1280,iw)\':-2',  # Only scale down if needed
            '-c:a', 'aac',  # AAC audio codec
            '-b:a', '96k',  # Lower audio bitrate (was 128k)
            '-ac', '2',  # Stereo audio
            '-movflags', '+faststart',  # Optimize for streaming
            '-threads', '0',  # Use all CPU cores
            '-y',  # Overwrite output
            output_path
        ]

        # Run with timeout of 120 seconds (2 minutes should be plenty for ultrafast)
        print(f"Running ffmpeg compression (max 2 minutes)...")
        result = subprocess.run(compress_cmd, check=True, capture_output=True, timeout=120)

        # Check output file size
        if os.path.exists(output_path):
            final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"Compression complete: {final_size_mb:.1f}MB")
            return True
        else:
            print("Compression failed: output file not created")
            return False

    except subprocess.TimeoutExpired:
        print(f"Compression timeout after 120 seconds")
        return False
    except Exception as e:
        print(f"Compression error: {e}")
        return False


@app.get("/")
async def root():
    """Serve the web application"""
    return FileResponse("public/index.html")


@app.post("/api/analyze-video-stream")
async def analyze_video_stream(
    video: UploadFile = File(...)
):
    """
    Analyze a video file and stream progress updates
    Uses Server-Sent Events (SSE) for real-time progress
    """
    async def generate():
        temp_video_path = None

        try:
            # Check API key
            from config import Config
            if not Config.GOOGLE_API_KEY:
                yield f"data: {json.dumps({'error': 'API key not configured'})}\n\n"
                return

            # Validate file type
            allowed_types = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/avi', 'video/mov']
            if video.content_type not in allowed_types and not video.content_type.startswith('video/'):
                yield f"data: {json.dumps({'error': 'Invalid file type. Please upload a video file (MP4, MOV, AVI, MKV)'})}\n\n"
                return

            # Send initial message
            yield f"data: {json.dumps({'status': 'Uploading video...'})}\n\n"
            await asyncio.sleep(0.1)

            # Save uploaded file
            file_size = 0
            temp_video_path = os.path.join("temp_uploads", f"temp_{datetime.now().timestamp()}_{video.filename}")

            with open(temp_video_path, "wb") as f:
                while chunk := await video.read(1024 * 1024):
                    file_size += len(chunk)
                    if file_size > 512 * 1024 * 1024:  # 512MB limit
                        yield f"data: {json.dumps({'error': 'Video too large (max 512MB)'})}\n\n"
                        return
                    f.write(chunk)

            yield f"data: {json.dumps({'status': f'Upload complete ({file_size/1024/1024:.1f}MB)'})}\n\n"
            await asyncio.sleep(0.1)

            # Compress if needed
            video_to_analyze = temp_video_path
            compressed_path = None

            if file_size > 20 * 1024 * 1024:  # If larger than 20MB, compress
                yield f"data: {json.dumps({'status': 'Video is large, compressing to under 20MB...'})}\n\n"
                await asyncio.sleep(0.1)

                compressed_path = temp_video_path.replace('.', '_compressed.')
                success = compress_video(temp_video_path, compressed_path)

                if success and os.path.exists(compressed_path):
                    compressed_size = os.path.getsize(compressed_path)
                    yield f"data: {json.dumps({'status': f'Compressed to {compressed_size/1024/1024:.1f}MB'})}\n\n"
                    video_to_analyze = compressed_path
                else:
                    yield f"data: {json.dumps({'error': 'Failed to compress video. Please upload a smaller file.'})}\n\n"
                    return

            # Verify video file size before sending to Gemini
            final_size = os.path.getsize(video_to_analyze) / (1024 * 1024)
            if final_size > 20:
                yield f"data: {json.dumps({'error': f'Video still too large ({final_size:.1f}MB). Please try a shorter video.'})}\n\n"
                return

            # Capture stdout to send progress messages
            yield f"data: {json.dumps({'status': 'Initializing analyzer...'})}\n\n"

            # Create analyzer
            analyzer = IterativeClipAnalyzer(
                model='pro',
                ontology_path='master_clip_ontology.pkl'
            )

            yield f"data: {json.dumps({'status': f'Sending video ({final_size:.1f}MB) to Gemini AI...'})}\n\n"
            yield f"data: {json.dumps({'status': 'This may take 5-10 minutes, please wait...'})}\n\n"
            await asyncio.sleep(0.1)

            # Process video with timeout - run in thread pool
            try:
                import concurrent.futures

                def run_analysis():
                    # Run analysis without capturing stdout (shows progress in server logs)
                    return analyzer.process_video(video_to_analyze, None)

                # Create thread pool and run with timeout
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_analysis)
                    try:
                        # Wait max 15 minutes for analysis
                        yield f"data: {json.dumps({'status': 'Processing with Gemini (timeout: 15min)...'})}\n\n"
                        result = future.result(timeout=900)  # 15 minutes

                        yield f"data: {json.dumps({'status': 'Analysis complete, reading results...'})}\n\n"

                    except concurrent.futures.TimeoutError:
                        yield f"data: {json.dumps({'error': 'Analysis timeout after 15 minutes. Video might be too long. Try a shorter video.'})}\n\n"
                        return
                    except Exception as e:
                        yield f"data: {json.dumps({'error': f'Analysis error: {str(e)}'})}\n\n"
                        return

            except Exception as e:
                yield f"data: {json.dumps({'error': f'Failed to start analysis: {str(e)}'})}\n\n"
                return

            # Read the output file content
            output_file_path = result.get('output', '')
            output_content = ''
            if output_file_path and os.path.exists(output_file_path):
                with open(output_file_path, 'r', encoding='utf-8') as f:
                    output_content = f.read()
            else:
                yield f"data: {json.dumps({'error': 'Analysis completed but no output file found'})}\n\n"
                return

            # Send final result
            yield f"data: {json.dumps({'success': True, 'output': output_content, 'status': 'Complete!'})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

        finally:
            # Cleanup temp files
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except:
                    pass
            if compressed_path and os.path.exists(compressed_path):
                try:
                    os.remove(compressed_path)
                except:
                    pass

    return StreamingResponse(generate(), media_type="text/event-stream")


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

        # Read the output file content
        output_file_path = result.get('output', '')
        output_content = 'Analysis complete'
        if output_file_path and os.path.exists(output_file_path):
            with open(output_file_path, 'r', encoding='utf-8') as f:
                output_content = f.read()

        return JSONResponse({
            "success": True,
            "output": output_content,
            "output_file": output_file_path,
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
    # Get port from environment variable (Railway) or default to 8000
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Video Analyzer Web App on port {port}...")
    print(f"Open http://localhost:{port} in your browser")
    uvicorn.run(app, host="0.0.0.0", port=port)
