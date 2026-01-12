# Video Analyzer - Web Deployment Guide

Deploy your Video Analyzer as a web application accessible to anyone online!

---

## 🌐 Deployment Options

We've configured your app for **multiple deployment platforms**. Choose the one that fits your needs:

| Platform | Best For | Free Tier | Difficulty | Deploy Time |
|----------|----------|-----------|------------|-------------|
| **Railway** | Full features, easiest | Yes (500 hrs/month) | ⭐ Easy | 5 min |
| **Render** | Reliable, simple | Yes (750 hrs/month) | ⭐ Easy | 5 min |
| **Heroku** | Classic, stable | Limited | ⭐⭐ Medium | 10 min |
| **Vercel** | Serverless, fast | Yes (generous) | ⭐⭐ Medium | 10 min |
| **Netlify** | Static + functions | Yes (100GB/month) | ⭐⭐⭐ Advanced | 15 min |
| **Google Cloud Run** | Scalable, pay-per-use | Yes ($300 credit) | ⭐⭐⭐ Advanced | 15 min |

**Recommended for beginners:** Railway or Render

---

## 🚀 Quick Start - Railway (Easiest)

### Step 1: Prepare Your Code

1. **Create a GitHub repository** (if you haven't already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_URL
   git push -u origin main
   ```

### Step 2: Deploy on Railway

1. Go to [Railway.app](https://railway.app/)
2. Click **"Start a New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select your video analyzer repository
6. Railway will automatically detect the Dockerfile and deploy!
7. Wait 3-5 minutes for deployment

### Step 3: That's It!

- Railway will give you a URL like: `https://your-app.up.railway.app`
- Share this URL with anyone!
- Users enter their own API keys (no server-side key needed)

**Cost:** Free for 500 hours/month. More than enough for personal use!

---

## 🎯 Quick Start - Render (Also Easy)

### Step 1: Push to GitHub

Same as Railway - ensure your code is on GitHub.

### Step 2: Deploy on Render

1. Go to [Render.com](https://render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will auto-detect your `render.yaml` configuration
5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment

### Step 3: Access Your App

- Render gives you a URL like: `https://your-app.onrender.com`
- Free tier: 750 hours/month
- Auto-sleeps after 15 min of inactivity (wakes up on first request)

---

## 📦 Deployment Files Explained

We've created these files for you:

### Core Web App Files

| File | Purpose |
|------|---------|
| `web_api.py` | Simplified FastAPI backend for web deployment |
| `public/index.html` | Beautiful web interface |
| `static/css/style.css` | Modern styling |
| `static/js/app.js` | Client-side JavaScript |
| `requirements_web.txt` | Minimal Python dependencies for web |

### Platform Configuration Files

| File | Platform | Purpose |
|------|----------|---------|
| `Dockerfile` | Railway, Render, Google Cloud | Container configuration |
| `railway.json` | Railway | Railway-specific settings |
| `render.yaml` | Render | Render-specific settings |
| `vercel.json` | Vercel | Serverless configuration |
| `netlify.toml` | Netlify | Static + functions config |

---

## 🔧 Detailed Deployment Guides

### Railway Deployment (Recommended)

**Why Railway?**
- Automatic HTTPS
- Auto-deploys on git push
- Simple environment variables
- Great free tier

**Steps:**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial deployment"
   git remote add origin https://github.com/YOUR_USERNAME/video-analyzer.git
   git push -u origin main
   ```

2. **Deploy on Railway:**
   - Visit [railway.app](https://railway.app/)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Dockerfile
   - Deploys automatically!

3. **Get Your URL:**
   - Go to Settings → Generate Domain
   - Copy your URL: `https://your-app.up.railway.app`

4. **Share with Users:**
   - Users visit your URL
   - They enter their own API keys
   - No server configuration needed!

**Cost:** Free for 500 hours/month (~20 days of 24/7 uptime)

---

### Render Deployment

**Why Render?**
- Generous free tier
- Auto-SSL certificates
- PostgreSQL database included (if needed later)

**Steps:**

1. **Push to GitHub** (same as Railway)

2. **Deploy on Render:**
   - Visit [render.com](https://render.com/)
   - Click "New +" → "Web Service"
   - Connect GitHub
   - Select your repository
   - Render reads `render.yaml` automatically
   - Click "Create Web Service"

3. **Configure:**
   - Build Command: `pip install -r requirements_web.txt`
   - Start Command: `uvicorn web_api:app --host 0.0.0.0 --port $PORT`
   - (Already in render.yaml - no manual config needed!)

4. **Access:**
   - URL: `https://your-app.onrender.com`
   - First request may be slow (app wakes from sleep)

**Cost:** Free tier with 750 hours/month

---

### Vercel Deployment (Serverless)

**Why Vercel?**
- Ultra-fast global CDN
- Serverless functions
- Great for static sites + API

**Steps:**

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy:**
   ```bash
   vercel
   ```

3. **Follow prompts:**
   - Link to existing project or create new
   - Vercel reads `vercel.json` config
   - Deploys automatically

4. **Production deployment:**
   ```bash
   vercel --prod
   ```

**Cost:** Free tier (generous limits)

**Note:** Vercel has cold start times for functions. First request may be slow.

---

### Google Cloud Run (Advanced)

**Why Cloud Run?**
- Pay only for what you use
- Auto-scales to zero
- Enterprise-grade

**Steps:**

1. **Install Google Cloud SDK:**
   - [Download here](https://cloud.google.com/sdk/docs/install)

2. **Authenticate:**
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Build and deploy:**
   ```bash
   gcloud run deploy video-analyzer \
     --source . \
     --region us-central1 \
     --allow-unauthenticated
   ```

4. **Access your URL:**
   - Google provides: `https://video-analyzer-xxxx.run.app`

**Cost:** Free tier + $300 credit. Very cheap after that (pay per request).

---

### Heroku Deployment

**Why Heroku?**
- Classic PaaS
- Lots of add-ons
- Proven reliability

**Steps:**

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku

   # Windows
   # Download from heroku.com
   ```

2. **Create Heroku app:**
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

4. **Open app:**
   ```bash
   heroku open
   ```

**Cost:** Free tier discontinued. Eco plan starts at $5/month.

---

## 🔐 Security & API Keys

### Important: User-Side API Keys

**Our deployment uses CLIENT-SIDE API keys:**
- Users enter their own Google Gemini API keys
- Keys stored in browser localStorage
- NEVER exposed to your server
- Each user pays for their own API usage

**Why this approach?**
✅ No server costs for API calls
✅ No rate limiting issues
✅ Users control their own usage
✅ Simple and secure

### Alternative: Server-Side API Key

If you want to provide a shared API key:

1. **Add environment variable** on your hosting platform:
   ```
   GOOGLE_API_KEY=your_key_here
   ```

2. **Update web_api.py:**
   ```python
   from config import Config

   # In analyze_video function:
   api_key = api_key or Config.GOOGLE_API_KEY
   ```

3. **Remove API key input** from frontend

**Warning:** You'll pay for all API usage. Set up billing alerts!

---

## 📊 Post-Deployment Checklist

After deploying, test these:

- [ ] Homepage loads correctly
- [ ] Video upload works (test with small video)
- [ ] API key can be entered and saved
- [ ] Video analysis completes
- [ ] Results display properly
- [ ] Download results works
- [ ] Data viewer buttons work (after first analysis)
- [ ] Mobile responsive design
- [ ] HTTPS is enabled (should be automatic)

---

## 🎨 Customization

### Change Colors/Branding

Edit `static/css/style.css`:

```css
:root {
    --primary-color: #YOUR_COLOR;
    --success-color: #YOUR_COLOR;
    /* etc. */
}
```

### Add Your Logo

Replace the emoji in `public/index.html`:

```html
<h1>
    <img src="/static/logo.png" alt="Logo" width="50">
    Video Analyzer
</h1>
```

### Custom Domain

Most platforms support custom domains:

**Railway:**
- Settings → Custom Domain → Add Domain

**Render:**
- Settings → Custom Domain → Add Domain

**Vercel:**
- Project Settings → Domains → Add Domain

---

## 🚨 Troubleshooting

### App Won't Deploy

**Check:**
- All files committed to git
- `requirements_web.txt` includes all dependencies
- Python version compatibility (we use 3.9)
- No syntax errors in code

### "Module Not Found" Error

**Fix:**
Add missing module to `requirements_web.txt`:
```bash
pip freeze | grep module-name >> requirements_web.txt
git add requirements_web.txt
git commit -m "Add missing dependency"
git push
```

### Video Upload Fails

**Possible causes:**
- Video over 20MB
- No API key entered
- Invalid API key
- Network timeout

**Check browser console** (F12) for error details.

### App is Slow

**Free tier limitations:**
- Apps "sleep" after inactivity
- First request wakes up the app (10-30 seconds)
- Subsequent requests are fast

**Solutions:**
- Upgrade to paid tier (stays always-on)
- Use a service like UptimeRobot to ping your app every 5 min
- Accept the slight delay on first load

### CORS Errors

Our API already has CORS enabled:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    ...
)
```

If you still see CORS errors, check your hosting platform's settings.

---

## 📈 Monitoring & Analytics

### Built-in Health Check

All platforms can monitor: `/api/health`

### Railway Monitoring

- Dashboard shows CPU, memory, requests
- Set up alerts for downtime

### Render Monitoring

- Free tier includes basic metrics
- Upgrade for advanced monitoring

### Add Google Analytics

Add to `public/index.html` before `</head>`:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR_GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR_GA_ID');
</script>
```

---

## 💰 Cost Estimates

### Free Tier Usage

| Scenario | Railway (500h) | Render (750h) | Cloud Run |
|----------|---------------|---------------|-----------|
| Personal use (2h/day) | FREE | FREE | FREE |
| Small team (8h/day) | FREE | FREE | ~$1/month |
| Public app (24/7) | $5-10/month | FREE (with sleep) | ~$5/month |

### Paid Plans

- **Railway:** $5/month for hobby, $20/month for pro
- **Render:** $7/month for starter
- **Heroku:** $5/month for eco, $25/month for basic
- **Cloud Run:** Pay per use (~$0.10 per 100k requests)

---

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push

**Railway & Render:**
- Automatically enabled!
- Push to GitHub → Auto-deploys

**Vercel:**
```bash
# Link project once:
vercel link

# Future deploys:
git push  # Vercel webhook auto-deploys
```

### Disable Auto-Deploy

**Railway:**
- Settings → Deploy Triggers → Disable

**Render:**
- Settings → Auto-Deploy → Disable

---

## 📱 Mobile Optimization

Our design is already mobile-responsive!

Test on mobile:
- Visit your deployed URL on phone
- Should work perfectly

To improve mobile experience further, edit `static/css/style.css`:

```css
@media (max-width: 768px) {
    /* Add mobile-specific styles */
}
```

---

## 🌍 Multi-Region Deployment

Deploy to multiple regions for global users:

**Cloud Run:**
```bash
# Deploy to multiple regions
gcloud run deploy --region us-central1
gcloud run deploy --region europe-west1
gcloud run deploy --region asia-east1
```

**Vercel:**
- Automatically deploys to global edge network!

---

## 📚 Additional Resources

### Documentation

- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)
- [Vercel Docs](https://vercel.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

### Support

- Railway Discord
- Render Community Forum
- Stack Overflow (tag: fastapi, deployment)

---

## ✅ Summary

**You now have everything needed to deploy your Video Analyzer online!**

**Recommended flow:**

1. **Test locally first:**
   ```bash
   python web_api.py
   # Visit http://localhost:8000
   ```

2. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Deploy on Railway** (easiest):
   - Connect GitHub
   - Auto-deploys!
   - Get public URL

4. **Share with users:**
   - They enter their API keys
   - Start analyzing videos!

**Total time:** ~10 minutes from start to deployed! 🎉

---

## 🎯 Next Steps

Once deployed:

1. **Test thoroughly** with different video sizes
2. **Share the URL** with friends/colleagues
3. **Monitor usage** in your hosting dashboard
4. **Customize branding** (colors, logo)
5. **Add analytics** (Google Analytics)
6. **Consider paid tier** if free tier limits reached
7. **Add custom domain** for professional look

**Questions?** Check the troubleshooting section or file an issue on GitHub!

---

**Happy deploying!** 🚀
