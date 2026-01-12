# 🚀 Quick Deploy - 5 Minutes to Live!

Get your Video Analyzer online in **5 minutes** with Railway (easiest option).

---

## Step 1: Test Locally (1 minute)

**Windows:**
```bash
start_web.bat
```

**macOS/Linux:**
```bash
./start_web.sh
```

Open http://localhost:8000 in your browser. If it works, proceed!

---

## Step 2: Push to GitHub (2 minutes)

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready to deploy"

# Create a repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/video-analyzer.git
git branch -M main
git push -u origin main
```

---

## Step 3: Deploy on Railway (2 minutes)

1. Go to **[railway.app](https://railway.app/)**
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your **video-analyzer** repository
5. Wait 3-5 minutes... ☕

**That's it!** Railway will give you a URL like:
```
https://video-analyzer-production-xxxx.up.railway.app
```

---

## Step 4: Share & Use

**Share your URL with anyone!**

Users will:
1. Visit your URL
2. Upload a video
3. Enter their Google Gemini API key (free from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey))
4. Click "Analyze Video"
5. Get results!

---

## Alternative: Render.com (Also Easy)

Same process, but use [render.com](https://render.com/):

1. Sign in with GitHub
2. Click **"New +"** → **"Web Service"**
3. Select your repository
4. Click **"Create Web Service"**
5. Done!

URL will be: `https://video-analyzer.onrender.com`

---

## Free Tier Limits

| Platform | Free Hours | Sleep After | Best For |
|----------|-----------|-------------|----------|
| Railway | 500h/month | No sleep | Active use |
| Render | 750h/month | 15 min idle | Any use |

Both are **more than enough** for personal/small team use!

---

## Troubleshooting

**App won't start?**
- Check requirements_web.txt has all dependencies
- Check Python version (we use 3.9)
- Check logs in Railway/Render dashboard

**Can't find GitHub repo?**
- Make sure you pushed all files
- Check repository is public (or grant Railway access to private repos)

**Need help?**
Read [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## What's Next?

Once deployed:
- ✅ Test with a small video
- ✅ Customize colors in `static/css/style.css`
- ✅ Add your logo
- ✅ Set up custom domain (optional)
- ✅ Share with the world!

---

**That's it! Your app is now online and accessible to anyone!** 🎉
