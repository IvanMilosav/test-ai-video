# 🎬 Video Analyzer - Complete Setup Guide

## ✅ Everything is Ready!

Your Video Analyzer can now be deployed as a web application using the API key from your `.env` file!

---

## 🚀 Quick Start (2 Steps)

### Step 1: Configure API Key

Create a `.env` file in this folder with your Google Gemini API key:

```bash
GOOGLE_API_KEY=your_api_key_here
```

**Get your API key (FREE):** [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Step 2: Start the Web App

**Windows:**
```bash
start_web.bat
```

**macOS/Linux:**
```bash
./start_web.sh
```

Then open http://localhost:8000 in your browser!

---

## 💡 How It Works

1. **Server uses `.env` file** - API key is stored securely on the server
2. **No browser-side API keys** - Users don't need to enter anything
3. **Simple for end users** - Just upload video and click analyze!

---

## 🌐 Deploy Online (Optional)

Want to share with others? Deploy to the cloud!

### Option 1: Railway (Easiest - 5 minutes)

1. Create `.env` file with your API key
2. Push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Deploy"
   git push origin main
   ```
3. Go to [railway.app](https://railway.app/)
4. Click "Deploy from GitHub"
5. Add environment variable: `GOOGLE_API_KEY=your_key`
6. Done! ✅

**Full guide:** [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

### Option 2: Render, Vercel, Google Cloud

All configuration files are ready:
- `Dockerfile` - For Railway, Render, Google Cloud Run
- `vercel.json` - For Vercel
- `render.yaml` - For Render
- `netlify.toml` - For Netlify

**Detailed guide:** [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md)

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| **`.env`** | Your API key (create this!) |
| `start_web.bat` | Windows launcher |
| `start_web.sh` | macOS/Linux launcher |
| `web_api.py` | Web server backend |
| `public/index.html` | Web interface |
| `static/` | CSS and JavaScript files |

---

## ⚙️ Configuration

### Setting Up .env File

Create a file named `.env` in this folder:

```bash
# Video Analyzer Configuration
GOOGLE_API_KEY=AIzaSyD...your_actual_key_here
```

**Don't commit `.env` to GitHub!** It's already in `.gitignore`.

### For Deployment

When deploying to cloud platforms:

1. **Don't include `.env` in your repository**
2. **Add API key as environment variable** in platform settings:
   - Railway: Settings → Variables → Add `GOOGLE_API_KEY`
   - Render: Environment → Add `GOOGLE_API_KEY`
   - Vercel: Settings → Environment Variables → Add `GOOGLE_API_KEY`

---

## 🎯 Features

### Web Interface
- 🎨 Beautiful, modern design
- 📱 Mobile-friendly
- 🔐 Secure (API key on server)
- 📊 View analysis history
- 💾 Download results
- 🚀 Fast and responsive

### Video Analysis
- AI-powered with Google Gemini
- Clip-by-clip breakdown
- Visual descriptions
- Automatic ontology building

---

## 🐛 Troubleshooting

### "API key not configured" error

**Solution:** Create `.env` file with your API key:
```bash
GOOGLE_API_KEY=your_key_here
```

### "Module not found" error

**Solution:** The startup scripts create a virtual environment automatically. If issues persist:

**Windows:**
```bash
rmdir /s /q .venv_web
start_web.bat
```

**macOS/Linux:**
```bash
rm -rf .venv_web
./start_web.sh
```

### "Video too large" error

**Solution:** Compress video to under 20MB using:
- [HandBrake](https://handbrake.fr/) (free, desktop app)
- Online compressor

### Server won't start

1. Check Python is installed: `python --version`
2. Make sure port 8000 is free
3. Check `.env` file exists and has valid API key

---

## 📖 Documentation

- **[START_WEB_APP.md](START_WEB_APP.md)** - Detailed setup guide
- **[QUICK_DEPLOY.md](QUICK_DEPLOY.md)** - 5-minute cloud deployment
- **[WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md)** - Complete deployment guide
- **[DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md)** - Overview of all options

---

## 🎉 You're All Set!

**To start locally:**
1. Create `.env` with your API key
2. Run `start_web.bat` (Windows) or `./start_web.sh` (Mac/Linux)
3. Open http://localhost:8000
4. Upload and analyze videos!

**To deploy online:**
1. Read [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
2. Takes 5 minutes on Railway!

---

## 💬 Questions?

Check the guides in this folder - everything is documented!

**Happy analyzing!** 🚀
