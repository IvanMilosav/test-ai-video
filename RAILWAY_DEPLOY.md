# 🚂 Railway Deployment Guide

## ✅ Fixed! Dockerfile Updated

The Dockerfile has been updated to include all required Python files.

---

## 🔄 Railway Auto-Redeploy

Railway automatically detects the git push and will redeploy within **3-5 minutes**.

### Watch the deployment:
1. Go to your Railway project
2. Click on your service
3. Click **"Deployments"** tab
4. Watch the build logs

---

## ⚙️ Required Environment Variable

Make sure you've added this in Railway:

**Variable Settings → New Variable:**
- **Key:** `GOOGLE_API_KEY`
- **Value:** Your Google Gemini API key

---

## 🔍 Check Deployment Status

### Build Logs Should Show:
```
✓ Building Dockerfile
✓ Installing dependencies from requirements_web.txt
✓ Copying application files
✓ Creating directories
✓ Starting uvicorn server
✓ Health check passed ✅
```

### If Health Check Still Fails:

1. **Check Logs:**
   - Click on your service
   - Go to **"Logs"** tab
   - Look for error messages

2. **Common Issues:**

   **Missing API Key:**
   ```
   Error: API key not configured
   ```
   **Fix:** Add `GOOGLE_API_KEY` in Variables tab

   **Port Issue:**
   ```
   Error: Address already in use
   ```
   **Fix:** Railway handles this automatically, just redeploy

   **Import Error:**
   ```
   ModuleNotFoundError: No module named 'X'
   ```
   **Fix:** Check if module is in `requirements_web.txt`

---

## 🎯 After Successful Deployment

1. **Get Your URL:**
   - Settings → Networking
   - Click "Generate Domain"
   - Copy the URL: `https://test-ai-video-production-xxxx.up.railway.app`

2. **Test It:**
   - Visit the URL in your browser
   - You should see the Video Analyzer interface
   - Try uploading a small video (< 5MB for first test)

3. **Share It:**
   - Send the URL to anyone
   - They can use it immediately
   - No setup required for end users!

---

## 📊 Monitor Your App

### Railway Dashboard Shows:
- **CPU Usage** - Should be low when idle
- **Memory** - ~200-300MB typical
- **Network** - Bandwidth used
- **Deployments** - History of builds

### Free Tier Limits:
- **500 hours/month** - About 20 days of 24/7 uptime
- **100GB bandwidth** - Plenty for testing
- **Shared CPU** - Good performance
- **512MB RAM** - Enough for this app

---

## 🐛 Troubleshooting

### App Won't Start

**Check:**
1. Environment variable `GOOGLE_API_KEY` is set
2. All Python files are in repository
3. `requirements_web.txt` has all dependencies
4. Dockerfile is correct (just fixed!)

**Fix:**
```bash
# Verify files locally first
python web_api.py
# Should start without errors
```

### Health Check Timeout

The health check hits `/api/health` endpoint.

**Verify locally:**
```bash
# Start server
python web_api.py

# In another terminal
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","version":"1.0.0"}
```

### Deployment Loop (Keeps Restarting)

**Causes:**
- App crashes on startup
- Missing dependency
- API key error

**Fix:**
- Check logs for crash reason
- Test locally first
- Ensure `.env` works locally

---

## 🔄 Redeploy

If you need to redeploy manually:

1. **From Railway Dashboard:**
   - Click on deployment
   - Click "Redeploy"

2. **From Git:**
   ```bash
   git commit --allow-empty -m "Trigger redeploy"
   git push origin main
   ```

---

## ✨ Success Indicators

When everything works:

✅ Build completes successfully
✅ Health check passes
✅ Service shows "Active"
✅ URL is accessible
✅ Web interface loads
✅ Can upload and analyze videos

---

## 🎉 Current Status

**Commit:** `Fix Dockerfile - add missing Python files`
**Files Updated:** Dockerfile now includes all Python modules
**Expected:** Deployment should succeed in 3-5 minutes

---

## 📞 Next Steps

1. **Wait 3-5 minutes** for Railway to redeploy
2. **Check deployment logs** for success
3. **Generate domain** if not already done
4. **Test the URL** with a small video
5. **Share your app!** 🚀

---

**The fix has been pushed. Railway is redeploying now!**
