# 🚀 Deploy to Netlify (Frontend Only)

This guide shows how to deploy the **frontend** to Netlify while keeping the **backend** on Railway.

## ⚠️ Important: Why Split Deployment?

**Netlify cannot run the video analysis backend** because:
- Function timeout: 10 seconds (free) / 26 seconds (Pro)
- Video analysis takes: 5-15 minutes
- No ffmpeg for video compression
- No persistent file storage

**Solution**: Frontend on Netlify + Backend on Railway ✅

---

## 📋 Prerequisites

1. ✅ Backend already deployed on Railway
2. ✅ Railway URL (e.g., `https://your-app.railway.app`)
3. ✅ Netlify account (free at netlify.com)

---

## 🎯 Quick Setup (3 Steps)

### Step 1: Create Config File

```bash
# Copy the example config
cp static/js/config.example.js static/js/config.js
```

Edit `static/js/config.js` and set your Railway backend URL:

```javascript
// Replace with your actual Railway URL
window.API_BASE_URL = 'https://your-app-name.railway.app';
```

**Example:**
```javascript
window.API_BASE_URL = 'https://ai-video-analyzer-production.railway.app';
```

### Step 2: Test Locally (Optional)

```bash
# Serve the public folder
cd public
python -m http.server 8080

# Open http://localhost:8080
# Should connect to Railway backend
```

### Step 3: Deploy to Netlify

#### Option A: Drag & Drop (Easiest)

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag the entire project folder OR just `public` + `static` folders
3. Wait for deploy (~30 seconds)
4. Done! ✅

#### Option B: GitHub Integration (Recommended)

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Add Netlify config"
   git push
   ```

2. Go to [app.netlify.com](https://app.netlify.com)

3. Click **"Add new site"** → **"Import an existing project"**

4. Connect your GitHub repository

5. Build settings:
   - **Build command:** (leave empty)
   - **Publish directory:** `public`

6. Click **"Deploy site"**

7. Done! ✅

---

## 🔧 Configuration

The `netlify.toml` file is already configured:

```toml
[build]
  publish = "public"

# Serve static files
[[redirects]]
  from = "/static/*"
  to = "/static/:splat"
  status = 200

# SPA fallback
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## ✅ Verify Deployment

1. Go to your Netlify URL (e.g., `https://your-site.netlify.app`)
2. Open browser DevTools → Console
3. You should see: `"No config.js - using same origin"` if config.js wasn't loaded
4. Upload a video and click "Analyze"
5. Check Network tab - requests should go to your Railway URL

---

## 🐛 Troubleshooting

### "Failed to fetch" or CORS errors

**Problem:** Railway backend not allowing Netlify frontend

**Solution:** CORS is already enabled in `web_api.py`:
```python
allow_origins=["*"]  # Allows all origins
```

If still having issues, check Railway logs.

### Config.js not loading

**Problem:** File not found or wrong path

**Solution:**
1. Make sure `static/js/config.js` exists
2. Check the URL in config.js is correct
3. Clear browser cache

### Netlify shows "Site not found"

**Problem:** Wrong publish directory

**Solution:**
1. Go to Site settings → Build & deploy
2. Set **Publish directory** to `public`
3. Redeploy

---

## 📊 Architecture

```
User Browser
    ↓
Netlify (Frontend)
  - HTML/CSS/JS
  - Static assets
  - CDN delivery
    ↓
Railway (Backend)
  - Python FastAPI
  - Video compression
  - Gemini API calls
  - Long-running analysis
```

---

## 💰 Costs

| Service | Tier | Cost | What's Included |
|---------|------|------|-----------------|
| **Netlify** | Free | $0 | 100GB bandwidth, 300 build min/month |
| **Railway** | Free | $0 | $5 credit/month (~500 hours) |
| **Total** | | **$0** | Plenty for personal use |

---

## 🚀 Next Steps

1. ✅ Deploy frontend to Netlify
2. ✅ Set custom domain (optional)
3. ✅ Enable HTTPS (automatic on Netlify)
4. ✅ Monitor Railway backend usage
5. ✅ Share your app!

---

## 📝 Files Changed

- `static/js/config.js` - Backend URL (create this file)
- `netlify.toml` - Netlify configuration (already exists)
- `public/index.html` - Loads config.js (already updated)
- `.gitignore` - Ignores config.js (already updated)

---

## 🎉 You're Done!

Your video analyzer is now:
- ✅ Frontend on Netlify (fast, global CDN)
- ✅ Backend on Railway (long-running processes)
- ✅ 100% free tier
- ✅ Production ready

**Share your app:** `https://your-site.netlify.app`
