# Video Analyzer - Simple User Guide

**For Non-Technical Users**

## What is Video Analyzer?

Video Analyzer is a desktop application that uses AI to analyze your videos and create detailed descriptions of what's happening in each scene.

---

## Quick Start (5 Minutes)

### Step 1: Get Your Free API Key

1. Go to: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. **Copy** the key (it looks like: `AIzaSyD-xxxxxxxxxxxxxxxxxxxxx`)

**Important:** Keep this key private - don't share it with others!

### Step 2: Set Up the Application

#### Windows Users:
1. **Find the file:** `simple_launcher.bat` in your Video Analyzer folder
2. **Before running it:** Create your configuration file:
   - Right-click on `.env.example` → Open with Notepad
   - Replace `your_api_key_here` with the API key you copied
   - Go to **File → Save As**
   - Change filename to: `.env` (just dot-env, nothing else)
   - Change "Save as type" to **"All Files"**
   - Click **Save**
3. **Double-click** `simple_launcher.bat`
4. Wait for the application to start (might take 30 seconds first time)

#### Mac Users:
1. Open **Terminal** (find it in Applications → Utilities)
2. Type: `cd ` (that's c-d-space)
3. **Drag** the Video Analyzer folder into the Terminal window
4. Press **Enter**
5. Create your `.env` file:
   - Type: `nano .env`
   - Type: `GOOGLE_API_KEY=` followed by your API key
   - Press **Control+X**, then **Y**, then **Enter**
6. Type: `./simple_launcher.sh`
7. Press **Enter**

---

## Using Video Analyzer

### Analyzing Your First Video

1. **Launch the app** (using the method above)
2. You'll see a window with a big folder icon
3. **Select your video:**
   - Click **"Browse Files"** button, OR
   - **Drag and drop** your video file into the window
4. Click **"Analyze Video"**
5. **Wait** (usually 1-3 minutes depending on video length)
6. When done, a popup will ask if you want to open the results folder
7. Click **"Yes"** to see your analysis!

### Supported Video Files

- **.mp4** (most common)
- **.mov** (iPhone/Mac videos)
- **.avi**
- **.mkv**

**Size limit:** 20MB - if your video is larger, you'll need to compress it first

---

## Understanding Your Results

After analysis, you'll get a text file with:

- **Clip-by-clip breakdown** of your video
- **Descriptions** of what's happening in each scene
- **Visual details** (colors, objects, people, actions)
- **Timestamps** for each clip

### Where to Find Results

Results are saved in the same folder as the app, with names like:
```
your_video_name_ontology_20260112_143022.txt
```

The numbers are the date and time (YYYYMMDD_HHMMSS).

---

## Viewing Your Data

Click the **"View Data"** menu at the top to see:

### 📊 Master Ontology (Statistics)
- Overall patterns from ALL videos you've analyzed
- Common objects, actions, scenes across all your videos
- Gets smarter as you analyze more videos!

### 🧠 Script-Clip Brain (Recipes)
- Real examples of "when the script says X, show Y"
- Useful for video editing guidance
- Builds up as you analyze more content

### 🎬 Recent Video Analyses
- List of all videos you've analyzed
- Click any one to see the detailed breakdown
- Organized by date (newest first)

---

## Troubleshooting

### "API key not configured" error

**Problem:** The app can't find your API key

**Solution:**
1. Make sure you created a file named exactly `.env` (not `.env.txt`)
2. Open the `.env` file - it should have:
   ```
   GOOGLE_API_KEY=your_actual_key_here
   ```
3. No spaces around the `=` sign
4. No quotes around the key

### "Video too large" error

**Problem:** Your video is over 20MB

**Solutions:**
1. **Use a video compressor:**
   - Windows: [HandBrake](https://handbrake.fr/) (free)
   - Mac: Already built into QuickTime (File → Export → 720p)
   - Online: [Clideo](https://clideo.com/compress-video) (free)

2. **Or trim your video:**
   - Only analyze the portion you need
   - Windows: Photos app
   - Mac: QuickTime (Edit → Trim)

### App won't start

**Windows:**
- Right-click `simple_launcher.bat` → **Run as administrator**
- Check if your antivirus blocked it (add exception)
- Make sure Python is installed: [python.org](https://www.python.org/downloads/)

**Mac:**
- If it says "unidentified developer":
  - Go to System Preferences → Security & Privacy
  - Click **"Open Anyway"**
- Make sure the script is executable:
  ```
  chmod +x simple_launcher.sh
  ```

### Analysis is very slow

**This is normal if:**
- Your internet is slow (AI processing happens in the cloud)
- Video is close to 20MB limit
- Many people are using Gemini API at the same time

**Speed it up:**
- Use a faster internet connection
- Compress your video to 5-10MB
- Try again during off-peak hours

### Can't find my output files

**Solution:**
1. Click **File → Open Output Folder** in the app
2. Or look in the same folder where the app is installed
3. Files are named: `videoname_ontology_YYYYMMDD_HHMMSS.txt`

---

## Tips for Best Results

### Video Quality
- **Clear footage** works best
- **Good lighting** helps the AI see details
- **Stable camera** (not too shaky)

### File Size
- **Aim for 5-15MB** for best balance of quality and speed
- Compress larger videos before analysis
- Can split long videos into shorter segments

### Organization
- **Name your videos clearly** before analyzing
- Results use the video filename
- Keep all related analyses in one folder

---

## Frequently Asked Questions

### Is my video uploaded somewhere?

Yes, temporarily. Your video is uploaded to Google's Gemini AI service for processing. Google's privacy policy applies. The video is processed and then discarded - not stored permanently.

### How much does it cost?

The Gemini API has a free tier that's usually enough for personal use. Check Google's current pricing if you plan to analyze many videos.

### Can I analyze multiple videos at once?

Currently, you need to analyze them one at a time. Just repeat the process for each video.

### What if I lose my API key?

1. Go back to [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. You can view your existing keys or create a new one
3. Update your `.env` file with the key

### Can I use this offline?

No, internet connection is required because the AI processing happens in Google's cloud.

### What languages are supported?

The app interface is in English. The AI can analyze videos in any language, but the analysis results will be in English.

---

## Getting Help

### If Something Goes Wrong

1. **Check this guide** - most issues are covered in Troubleshooting
2. **Check the error message** - it usually tells you what's wrong
3. **Try restarting** the application
4. **Check your internet** connection

### Still Need Help?

Look for:
- `TROUBLESHOOTING.txt` file
- `README.md` file
- Support contact in the main README

---

## Privacy & Security

### Your API Key
- Keep it private (like a password)
- Don't share screenshots that show your key
- Don't commit `.env` file to public GitHub repositories

### Your Videos
- Sent to Google Gemini AI for processing
- Subject to Google's privacy policy
- Not stored permanently by Google
- Not stored permanently by this app (only the analysis text)

### Your Analysis Results
- Stored locally on your computer
- You control the files
- Can delete anytime

---

## Keyboard Shortcuts

- **Ctrl+O** (Cmd+O on Mac): Open video file
- **Alt+F4** (Cmd+Q on Mac): Quit application
- **F1**: Help (if implemented)

---

## What's Next?

Once you're comfortable with basic analysis:

1. **Try different videos** - see how the AI handles different content
2. **Check the Master Ontology** - see patterns across all your videos
3. **Use the Script-Clip Brain** - learn from real examples
4. **Organize your analyses** - create folders for different projects

---

## Quick Reference Card

**To analyze a video:**
1. Launch app (double-click `simple_launcher.bat` or run `./simple_launcher.sh`)
2. Browse or drag-drop video
3. Click "Analyze Video"
4. Wait for completion
5. View results

**To view past analyses:**
- Menu → View Data → Recent Video Analyses

**To find output files:**
- Menu → File → Open Output Folder

**Need to change API key:**
- Edit `.env` file in Notepad/TextEdit

---

**You're all set! Start analyzing your videos!** 🎬

If you get stuck, check the Troubleshooting section or the detailed DEPLOYMENT_GUIDE.md for more technical information.
