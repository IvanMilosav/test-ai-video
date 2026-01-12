# Dockerfile for containerized deployment (Railway, Render, etc.)

FROM python:3.9-slim

WORKDIR /app

# Install dependencies
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
COPY public/ ./public/
COPY static/ ./static/

# Create necessary directories
RUN mkdir -p temp_uploads outputs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "web_api:app", "--host", "0.0.0.0", "--port", "8000"]
