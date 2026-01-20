# Video Analyzer - Web Application

AI-powered video analysis using Google Gemini API, deployed to Railway.

## 🚀 Features

- Upload videos up to 200MB
- Automatic compression for videos > 100MB
- Real-time analysis progress updates
- Structured clip ontology generation
- RESTful API with streaming responses

## 📋 Essential Files

### Core Application
- `web_api.py` - FastAPI server with video upload and analysis
- `iterative_analyzer.py` - Gemini AI video analyzer
- `clip_ontology_schema.py` - Data structures for clip ontology
- `script_clip_brain.py` - Script and clip brain storage
- `config.py` - Configuration and API key management

### Frontend
- `public/index.html` - Main web interface
- `static/css/style.css` - Styling
- `static/js/app.js` - Frontend JavaScript with SSE streaming

### Deployment
- `Dockerfile` - Docker container configuration
- `railway.json` - Railway deployment config
- `requirements_web.txt` - Python dependencies
- `.env.example` - Environment variables template

### Data
- `master_clip_ontology.txt` - Master ontology (text format)
- `master_clip_ontology.pkl` - Master ontology (binary)
- `script_clip_brain.txt` - Brain database (text format)
- `script_clip_brain.pkl` - Brain database (binary)

## 🛠️ Setup

### 1. Install Dependencies

```bash
pip install -r requirements_web.txt
```

### 2. Configure API Key

Create `.env` file:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Run Locally

```bash
python web_api.py
```

Visit: http://localhost:8000

## 🌐 Deploy to Railway

1. Push this repo to GitHub
2. Connect to Railway
3. Add environment variable: `GOOGLE_API_KEY`
4. Deploy automatically

See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for detailed instructions.

## 📊 File Size Limits

- **Max upload:** 200MB
- **Compression threshold:** 100MB
- **Compression target:** 90MB
- **Videos < 100MB:** No compression (sent directly to Gemini)
- **Videos 100-200MB:** Compressed to ~90MB

## 🔧 API Endpoints

### `POST /api/analyze-video-stream`
Upload and analyze video with real-time progress updates via Server-Sent Events.

**Parameters:**
- `video` (file): Video file to analyze

**Response:** SSE stream with progress updates and final results

### `GET /api/data/{type}`
Retrieve ontology or brain data.

**Types:** `master-ontology`, `script-clip-brain`, `history`

## 📝 License

MIT
