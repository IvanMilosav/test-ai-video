# 🎬 Video Analyzer - Web Edition

**AI-Powered Video Analysis - Now Online!**

Analyze videos with Google Gemini AI through a beautiful web interface. Deploy in minutes, use anywhere!

---

## ✨ Features

- 🌐 **Web-based** - Access from any browser
- 📱 **Mobile-friendly** - Works on phones and tablets
- 🎨 **Beautiful UI** - Modern, clean design
- 🚀 **Easy deployment** - Deploy to Railway, Render, Vercel, etc.
- 🔐 **Secure** - Users provide their own API keys
- 💰 **Cost-effective** - Free tier available on most platforms
- 📊 **Data viewer** - View analysis history and insights

---

## 🎯 Quick Start

### Option 1: Deploy Online (Recommended)

**Deploy to Railway in 5 minutes:**

1. Push this code to GitHub
2. Go to [railway.app](https://railway.app/)
3. Click "Deploy from GitHub"
4. Select this repository
5. Wait for deployment
6. Get your public URL!

**Full guide:** [QUICK_DEPLOY.md](QUICK_DEPLOY.md)

### Option 2: Run Locally

```bash
# Install dependencies
pip install -r requirements_web.txt

# Run the web app
python web_api.py

# Open browser
open http://localhost:8000
```

---

## 📂 File Structure

```
video-analyzer/
├── Web Application
│   ├── public/
│   │   └── index.html              # Main web interface
│   ├── static/
│   │   ├── css/style.css           # Styling
│   │   └── js/app.js               # Client-side logic
│   └── web_api.py                  # FastAPI backend
│
├── Deployment Configurations
│   ├── Dockerfile                  # Container config
│   ├── railway.json                # Railway config
│   ├── render.yaml                 # Render config
│   ├── vercel.json                 # Vercel config
│   └── netlify.toml                # Netlify config
│
├── Documentation
│   ├── WEB_DEPLOYMENT_GUIDE.md     # Detailed deployment guide
│   ├── QUICK_DEPLOY.md             # 5-minute deployment
│   └── README_WEB.md               # This file
│
└── Core Application
    ├── iterative_analyzer.py       # Video analysis engine
    ├── gemini_analyzer.py          # Gemini AI integration
    └── requirements_web.txt        # Python dependencies
```

---

## 🚀 Deployment Options

We support **multiple platforms**. Choose what works best for you:

### 🏆 Recommended: Railway

**Why Railway?**
- ✅ Easiest to deploy
- ✅ 500 hours/month free
- ✅ Auto-deploys on git push
- ✅ Built-in HTTPS

**Deploy:** [Follow QUICK_DEPLOY.md](QUICK_DEPLOY.md)

### 🌟 Also Great: Render

**Why Render?**
- ✅ 750 hours/month free
- ✅ Simple setup
- ✅ PostgreSQL included (if needed)

**Deploy:** Same as Railway, just use [render.com](https://render.com/)

### ⚡ Advanced Options

- **Vercel** - Serverless, global CDN
- **Google Cloud Run** - Pay-per-use, auto-scaling
- **Heroku** - Classic PaaS (paid only now)

**Full guides:** [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md)

---

## 🔐 Security & API Keys

### User-Provided API Keys (Default)

Users enter their own Google Gemini API keys:
- Stored in browser localStorage
- Never sent to your server
- Each user controls their own usage
- No cost to you!

**Get API key:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### Server-Side API Key (Optional)

If you want to provide a shared API key:

1. Set environment variable on your hosting platform:
   ```
   GOOGLE_API_KEY=your_key_here
   ```

2. Users won't need to enter keys

**Warning:** You'll pay for all API usage!

---

## 📖 How to Use (For End Users)

1. **Visit the web app** (your deployed URL)
2. **Upload a video** (MP4, MOV, AVI, MKV - max 20MB)
3. **Enter your API key** (one-time setup)
4. **Click "Analyze Video"**
5. **Wait 1-3 minutes** for AI analysis
6. **View results** and download!

**Need to compress videos?** Use [HandBrake](https://handbrake.fr/) (free)

---

## 🎨 Customization

### Change Colors

Edit `static/css/style.css`:

```css
:root {
    --primary-color: #4a9eff;  /* Change to your brand color */
    --success-color: #28a745;
}
```

### Add Your Logo

Edit `public/index.html`:

```html
<header>
    <img src="/static/logo.png" alt="Logo" width="60">
    <h1>Your App Name</h1>
</header>
```

### Custom Domain

Configure in your hosting platform:
- Railway: Settings → Custom Domain
- Render: Settings → Custom Domain
- Vercel: Project Settings → Domains

---

## 📊 Features in Detail

### Video Analysis

- **AI-powered** with Google Gemini
- **Clip-by-clip breakdown** of video content
- **Visual descriptions** for each scene
- **Automatic ontology building** from multiple videos

### Data Viewer

Access historical data:
- **Master Ontology** - Patterns across all analyzed videos
- **Script-Clip Brain** - Real examples of visual storytelling
- **Analysis History** - All your past video analyses

### Mobile Support

- Fully responsive design
- Works on phones, tablets, desktops
- Touch-friendly interface
- Optimized for small screens

---

## 🔧 Development

### Running Locally

```bash
# Install dependencies
pip install -r requirements_web.txt

# Run development server
python web_api.py

# Server will start at http://localhost:8000
```

### Making Changes

1. Edit files as needed
2. Test locally
3. Commit and push to GitHub
4. Railway/Render auto-deploys!

### Testing

```bash
# Test with curl
curl -X POST http://localhost:8000/api/health

# Should return: {"status":"healthy","version":"1.0.0"}
```

---

## 🚨 Troubleshooting

### Common Issues

**"Video too large" error**
- Compress video to under 20MB
- Use HandBrake or online compressor

**"API key not configured" error**
- Make sure you entered a valid API key
- Get new key from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

**App is slow**
- Free tier apps "sleep" after inactivity
- First request wakes the app (10-30 seconds)
- Subsequent requests are fast

**Can't upload video**
- Check browser console (F12) for errors
- Ensure video is under 20MB
- Try different browser

### Getting Help

1. Check [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md)
2. Check hosting platform logs
3. File an issue on GitHub

---

## 💰 Cost Breakdown

### Free Tier (Recommended)

| Platform | Free Allowance | Good For |
|----------|---------------|----------|
| Railway | 500 hours/month | Personal use, small teams |
| Render | 750 hours/month | Any use (with sleep) |
| Vercel | Generous limits | Low to medium traffic |
| Cloud Run | $300 credit | Testing, low traffic |

**Free tier is perfect for:**
- Personal projects
- Small teams (< 10 people)
- Portfolio/demo apps
- Learning and testing

### Paid Tiers

Only needed if you exceed free limits:

- **Railway:** $5/month (hobby), $20/month (pro)
- **Render:** $7/month (no sleep, always-on)
- **Cloud Run:** Pay per use (~$5-10/month for moderate use)

**Most users stay on free tier!**

---

## 📈 Scaling

Your app can handle:

**Free tier:**
- ~10-50 analyses per day
- 100s of page views
- 5-10 concurrent users

**Paid tier:**
- Unlimited analyses
- 1000s of page views
- 100+ concurrent users
- Auto-scales with demand

---

## 🌍 Use Cases

### Personal Use
- Analyze your own videos
- Build a knowledge base
- Learn about AI video analysis

### Small Teams
- Share one deployed app
- Each team member uses their own API key
- Collaborate on video projects

### Public Service
- Offer video analysis as a service
- Users bring their own API keys
- No cost to you!

### Education
- Teach AI/ML concepts
- Demonstrate video analysis
- Student projects

---

## 🔄 Updates & Maintenance

### Auto-Updates (Railway/Render)

1. Make changes locally
2. Commit and push to GitHub
3. App automatically redeploys!

No manual intervention needed.

### Manual Updates

1. Make changes
2. Push to GitHub
3. Redeploy from platform dashboard

---

## 📚 Tech Stack

- **Backend:** FastAPI (Python)
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **AI:** Google Gemini API
- **Deployment:** Docker, Railway, Render, Vercel
- **Storage:** Local filesystem (analyses saved as text files)

---

## 🤝 Contributing

Want to improve the web app?

1. Fork the repository
2. Make your changes
3. Test locally
4. Submit a pull request

**Ideas for contributions:**
- UI improvements
- New features (batch upload, video preview, etc.)
- Better mobile experience
- Internationalization
- Dark mode toggle

---

## 📄 License

[Your license here]

---

## 🎉 Success Stories

**Deploy your app and share your experience!**

Once deployed, you'll have:
- ✅ A live web application
- ✅ Public URL to share
- ✅ AI video analysis for anyone
- ✅ Zero ongoing maintenance
- ✅ Professional portfolio piece

---

## 🔗 Quick Links

- **Deploy Now:** [QUICK_DEPLOY.md](QUICK_DEPLOY.md) (5 minutes!)
- **Full Guide:** [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md)
- **Railway:** [railway.app](https://railway.app/)
- **Render:** [render.com](https://render.com/)
- **Get API Key:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

## ⭐ Star This Repo!

If you find this useful, give it a star on GitHub!

---

**Ready to deploy?** Start with [QUICK_DEPLOY.md](QUICK_DEPLOY.md) - your app will be online in 5 minutes! 🚀

**Questions?** Check [WEB_DEPLOYMENT_GUIDE.md](WEB_DEPLOYMENT_GUIDE.md) or file an issue!
