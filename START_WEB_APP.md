# 🚀 Start Your Video Analyzer Web App

## Quick Start - Local Testing

### Windows Users

1. **Double-click** `start_web.bat`
2. Wait for server to start (about 10-20 seconds)
3. **Open browser** to http://localhost:8000
4. **Start analyzing videos!**

### macOS/Linux Users

1. **Open Terminal** in this folder
2. Run: `./start_web.sh`
3. Wait for server to start
4. **Open browser** to http://localhost:8000
5. **Start analyzing videos!**

---

## First Time Using the Web App?

### Step 1: Get Your API Key (2 minutes)

1. Go to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with Google
3. Click **"Create API Key"**
4. **Copy** the key

### Step 2: Use the Web App

1. **Upload a video** (MP4, MOV, AVI, MKV - max 20MB)
2. **Enter your API key** (you'll only need to do this once)
3. Click **"Analyze Video"**
4. Wait 1-3 minutes for AI analysis
5. **View and download** your results!

---

## Troubleshooting

### "Module not found" or Import Errors

The startup scripts automatically create a virtual environment and install dependencies. If you still see errors:

**Windows:**
```bash
# Delete the old environment
rmdir /s /q .venv_web

# Run start_web.bat again
start_web.bat
```

**macOS/Linux:**
```bash
# Delete the old environment
rm -rf .venv_web

# Run start_web.sh again
./start_web.sh
```

### Can't Upload Video

- Make sure video is under 20MB
- Use HandBrake to compress: [https://handbrake.fr/](https://handbrake.fr/)
- Try a different browser (Chrome/Firefox recommended)

### Server Won't Start

1. **Check Python is installed:**
   ```bash
   python --version
   # or
   python3 --version
   ```

2. **Make sure port 8000 is available:**
   - Close any other applications using port 8000
   - Or edit `web_api.py` and change the port number

3. **Check for errors:**
   - Read the error messages in the terminal
   - Most common: missing Python or pip

---

## Deploy Online (Optional)

Want to share your app with others? Deploy it online!

1. **Read** [QUICK_DEPLOY.md](QUICK_DEPLOY.md) for 5-minute deployment
2. **Or read** [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md) for detailed guide

**Recommended platforms:**
- **Railway** - 500 hours/month free, easiest to deploy
- **Render** - 750 hours/month free, simple setup

---

## What's Next?

Once you have it running:

- ✅ Analyze your first video
- ✅ Check out the "View Data" section
- ✅ Customize the colors in `static/css/style.css`
- ✅ Deploy online to share with others!

---

## Need More Help?

- **User Guide:** [USER_GUIDE_SIMPLE.md](USER_GUIDE_SIMPLE.md)
- **Web Deployment:** [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md)
- **Quick Deploy:** [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

---

**Ready? Double-click `start_web.bat` (Windows) or run `./start_web.sh` (macOS/Linux)!** 🎉
