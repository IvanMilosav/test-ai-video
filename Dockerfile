# Dockerfile for containerized deployment (Railway, Render, etc.)
# Updated to handle PORT environment variable correctly

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies (ffmpeg for video compression)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements_web.txt .
RUN pip install --no-cache-dir -r requirements_web.txt

# Copy application files
COPY web_api.py .
COPY config.py .
COPY iterative_analyzer.py .
COPY gemini_analyzer.py .
COPY analyze_video.py .
COPY brain_synthesizer.py .
COPY ontology_reporter.py .
COPY clip_ontology_schema.py .
COPY script_clip_brain.py .
COPY public/ ./public/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p temp_uploads outputs

# Expose port
EXPOSE 8000

# Run the application
# Python will read PORT from environment variable
CMD ["python", "web_api.py"]
