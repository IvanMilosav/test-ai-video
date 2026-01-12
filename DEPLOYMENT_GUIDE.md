# Video Analyzer - Deployment Guide for Non-Technical Users

This guide explains how to distribute and deploy the Video Analyzer GUI application so that non-technical users can easily use it.

## Table of Contents

1. [Quick Start - For Users](#quick-start---for-users)
2. [Deployment Options](#deployment-options)
3. [Building Installers](#building-installers)
4. [Distribution Methods](#distribution-methods)
5. [User Setup Instructions](#user-setup-instructions)

---

## Quick Start - For Users

### Windows Users

**Option 1: Simple Launcher (Recommended for most users)**
1. Download the project folder
2. Get a Google Gemini API key from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
3. Create a file named `.env` in the project folder
4. Add your API key: `GOOGLE_API_KEY=your_key_here`
5. Double-click `simple_launcher.bat`

**Option 2: Portable Version (No installation needed)**
1. Download `VideoAnalyzer-Portable.zip`
2. Extract anywhere on your computer
3. Create `.env` file with your API key
4. Double-click `VideoAnalyzer.exe`

**Option 3: Installer (Most professional)**
1. Download `VideoAnalyzer-Setup.exe`
2. Run the installer
3. Enter your API key during installation
4. Launch from Start Menu or Desktop shortcut

### macOS Users

**Option 1: Simple Launcher**
1. Download the project folder
2. Get your API key from [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
3. Create `.env` file with your API key
4. Open Terminal in the project folder
5. Run: `./simple_launcher.sh`

**Option 2: App Bundle**
1. Download `VideoAnalyzer.dmg`
2. Open the DMG file
3. Drag VideoAnalyzer to Applications
4. Right-click the app → Open (first time only)
5. Create `.env` file in the app's folder

### Linux Users

**Option 1: Simple Launcher**
1. Download the project folder
2. Get your API key
3. Create `.env` file
4. Run: `./simple_launcher.sh`

**Option 2: AppImage**
1. Download `VideoAnalyzer.AppImage`
2. Make executable: `chmod +x VideoAnalyzer.AppImage`
3. Run: `./VideoAnalyzer.AppImage`

---

## Deployment Options

### Option 1: Simple Launcher Scripts (Easiest to Create)

**Pros:**
- No build process needed
- Easy to update
- Users can see and modify the code
- Works on all platforms

**Cons:**
- Requires Python installation
- Users see technical setup process
- Larger download size

**Best for:**
- Developer/technical teams
- Organizations with IT support
- Beta testing

**Files to distribute:**
- Entire project folder
- `simple_launcher.bat` (Windows) or `simple_launcher.sh` (macOS/Linux)
- `.env.example` (users copy to `.env`)
- Instructions document

### Option 2: Portable Executable (Good Balance)

**Pros:**
- No installation required
- Single executable file
- No Python needed
- Smaller download

**Cons:**
- Requires build process
- Larger file size than installer
- May trigger antivirus warnings

**Best for:**
- Small-scale distribution
- USB drive deployment
- Users without admin rights

**How to create:** See [Building Installers](#building-installers)

### Option 3: Professional Installer (Most User-Friendly)

**Pros:**
- Most professional appearance
- Guided setup process
- Creates shortcuts automatically
- Uninstaller included
- Can collect API key during installation

**Cons:**
- Most complex to create
- Requires admin rights to install
- Platform-specific

**Best for:**
- Public release
- Large organizations
- Non-technical end users

**How to create:** See [Building Installers](#building-installers)

---

## Building Installers

### Prerequisites

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **Prepare Assets:**
   - Ensure `icon.ico` and `icon.png` exist
   - Have `.env.example` ready
   - Include documentation files

### Build All Distribution Files

Run the automated build script:

```bash
python build_installer.py
```

This creates:
- Standalone executable in `dist/`
- Portable package in `portable/VideoAnalyzer-Portable.zip`
- Installer scripts (platform-specific)

### Manual Build Steps

#### 1. Build Standalone Executable

```bash
# Clean previous builds
rm -rf build dist

# Build with PyInstaller
pyinstaller video_analyzer.spec --clean
```

Output: `dist/VideoAnalyzer.exe` (Windows) or `dist/VideoAnalyzer` (macOS/Linux)

#### 2. Create Portable Package

```bash
python build_installer.py
```

Or manually:
```bash
mkdir -p portable/VideoAnalyzer
cp dist/VideoAnalyzer.exe portable/VideoAnalyzer/
cp icon.* portable/VideoAnalyzer/
cp .env.example portable/VideoAnalyzer/
# Create README and launcher scripts
cd portable && zip -r VideoAnalyzer-Portable.zip VideoAnalyzer/
```

#### 3. Create Windows Installer

**Using Inno Setup:**

1. Download [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the executable first
3. Compile the installer:
   ```bash
   iscc video_analyzer.iss
   ```
4. Find installer: `installer/VideoAnalyzer-Setup.exe`

#### 4. Create macOS DMG

```bash
./create_dmg.sh
```

This creates `VideoAnalyzer-Installer.dmg`

#### 5. Create Linux AppImage

For Linux, the portable executable works well, or you can create a .deb package:

```bash
# Install tools
sudo apt install dpkg-dev

# Create package structure
mkdir -p video-analyzer_1.0.0/DEBIAN
mkdir -p video-analyzer_1.0.0/usr/local/bin
mkdir -p video-analyzer_1.0.0/usr/share/applications

# Copy files and create package
# (See detailed AppImage guide online)
```

---

## Distribution Methods

### 1. Direct Download (Simplest)

**Setup:**
1. Upload files to Google Drive, Dropbox, or file hosting
2. Share download link
3. Include README with setup instructions

**Best for:** Small teams, trusted users

### 2. GitHub Releases (Recommended)

**Setup:**
1. Create GitHub repository
2. Build all installers
3. Create a release with:
   - Windows installer (.exe)
   - macOS DMG
   - Portable ZIP
   - Linux AppImage/tar.gz
4. Write detailed release notes

**Example release assets:**
```
VideoAnalyzer-Setup-Windows.exe     (15 MB)
VideoAnalyzer-macOS.dmg             (18 MB)
VideoAnalyzer-Portable.zip          (12 MB)
VideoAnalyzer-Linux.AppImage        (20 MB)
```

### 3. Website Distribution

Create a simple website with:
- Download buttons for each platform
- Setup instructions
- Video tutorial
- FAQ section

### 4. Internal Distribution

For organizations:
1. Deploy via software management (SCCM, Jamf, etc.)
2. Share on internal network drive
3. Include in employee onboarding

---

## User Setup Instructions

### Creating User-Friendly Documentation

Include these sections in your user guide:

#### 1. System Requirements

```
Minimum Requirements:
- Windows 10/11, macOS 10.14+, or Linux
- 4GB RAM
- Internet connection
- 200MB free disk space

Recommended:
- 8GB RAM
- Fast internet connection
```

#### 2. Installation Steps

**For Installer Version:**

```
1. Download VideoAnalyzer-Setup.exe
2. Double-click to run
3. Follow the installation wizard
4. When prompted, enter your Google Gemini API key
   (Get it from: https://aistudio.google.com/app/apikey)
5. Click Install
6. Launch from Desktop shortcut
```

**For Portable Version:**

```
1. Download VideoAnalyzer-Portable.zip
2. Extract to any folder (e.g., Desktop, Documents)
3. Open the VideoAnalyzer folder
4. Right-click on ".env.example" → Open with Notepad
5. Replace "your_api_key_here" with your actual API key
6. Save as ".env" (remove .example)
7. Double-click "VideoAnalyzer.exe"
```

#### 3. Getting API Key

Create step-by-step guide with screenshots:

```
HOW TO GET YOUR FREE API KEY:

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (looks like: AIzaSyD-xxxxxxxxxxxxxxxxxxxxx)
5. Paste it in your .env file

Important: Keep your API key private!
```

#### 4. Using the Application

```
STEP 1: SELECT VIDEO
- Click "Browse Files" button
- Or drag & drop a video file into the window
- Supported: MP4, MOV, AVI, MKV (under 20MB)

STEP 2: ANALYZE
- Click "Analyze Video" button
- Wait for the progress bar to complete (1-3 minutes)
- A success message will appear when done

STEP 3: VIEW RESULTS
- Click "Yes" to open the output folder
- Or use menu: View Data → Recent Video Analyses
- Results saved as text files with timestamps
```

#### 5. Troubleshooting

```
PROBLEM: "API key not found" error
SOLUTION: Make sure .env file exists and has: GOOGLE_API_KEY=your_key

PROBLEM: "Video too large" error
SOLUTION: Compress your video to under 20MB using HandBrake or similar

PROBLEM: App won't start
SOLUTION:
- Windows: Right-click → Run as Administrator
- macOS: System Preferences → Security → Allow app
- Check antivirus isn't blocking it

PROBLEM: Slow analysis
SOLUTION:
- Check internet connection
- Try smaller video file
- Close other applications

PROBLEM: Can't find output files
SOLUTION: Use menu → File → Open Output Folder
```

---

## Complete Distribution Checklist

### Files to Include

- [ ] Application executable or installer
- [ ] `.env.example` file
- [ ] `README.txt` or `USER_GUIDE.pdf`
- [ ] `TROUBLESHOOTING.txt`
- [ ] Sample video (optional)
- [ ] Icon files (for shortcuts)
- [ ] License file (if applicable)

### Documentation to Provide

- [ ] System requirements
- [ ] Installation instructions
- [ ] API key setup guide
- [ ] Usage tutorial
- [ ] Troubleshooting guide
- [ ] FAQ
- [ ] Contact/support information

### Testing Before Distribution

- [ ] Test on clean Windows 10/11 machine
- [ ] Test on macOS (multiple versions if possible)
- [ ] Test on Linux (Ubuntu/Fedora)
- [ ] Verify API key setup process
- [ ] Test with various video formats
- [ ] Check error messages are clear
- [ ] Verify output files are created correctly
- [ ] Test all menu options
- [ ] Check uninstaller works (if applicable)

### Support Setup

- [ ] Create FAQ document
- [ ] Set up email support address
- [ ] Create GitHub Issues page (for bug reports)
- [ ] Prepare video tutorials
- [ ] Create knowledge base or wiki

---

## Example Distribution Package

### Folder Structure

```
VideoAnalyzer-v1.0.0/
├── Windows/
│   ├── VideoAnalyzer-Setup.exe       (Installer)
│   └── VideoAnalyzer-Portable.zip    (Portable version)
├── macOS/
│   ├── VideoAnalyzer.dmg             (Mac installer)
│   └── VideoAnalyzer.app.zip         (Portable app)
├── Linux/
│   ├── VideoAnalyzer.AppImage        (Portable)
│   └── video-analyzer_1.0.0.deb      (Debian package)
├── Documentation/
│   ├── USER_GUIDE.pdf
│   ├── QUICK_START.txt
│   ├── API_KEY_SETUP.pdf
│   └── TROUBLESHOOTING.txt
├── README.txt                         (Start here)
└── sample_video.mp4                   (Optional)
```

### README.txt Template

```
═══════════════════════════════════════════════════════
  VIDEO ANALYZER - AI-Powered Video Analysis Tool
═══════════════════════════════════════════════════════

Thank you for downloading Video Analyzer!

CHOOSE YOUR PLATFORM:
  • Windows users → Open the "Windows" folder
  • Mac users → Open the "macOS" folder
  • Linux users → Open the "Linux" folder

FIRST TIME SETUP (5 minutes):
  1. Install the application (or use portable version)
  2. Get your FREE API key from:
     https://aistudio.google.com/app/apikey
  3. Follow the setup wizard or create .env file
  4. You're ready to analyze videos!

NEED HELP?
  • Read: Documentation/QUICK_START.txt
  • Full guide: Documentation/USER_GUIDE.pdf
  • Problems? Documentation/TROUBLESHOOTING.txt
  • Email: support@yourapp.com

QUICK START:
  1. Launch Video Analyzer
  2. Click "Browse Files" and select a video
  3. Click "Analyze Video"
  4. View results when complete!

Enjoy analyzing your videos!
```

---

## Advanced: Auto-Update System

For professional deployments, consider adding auto-update:

### Simple Version Check

Add to your app:

```python
import requests

def check_for_updates():
    try:
        response = requests.get("https://yoursite.com/version.json")
        latest = response.json()["version"]
        current = "1.0.0"
        if latest > current:
            return True, latest
    except:
        pass
    return False, None
```

### GitHub Releases Integration

```python
def check_github_releases():
    url = "https://api.github.com/repos/yourusername/video-analyzer/releases/latest"
    response = requests.get(url)
    latest_version = response.json()["tag_name"]
    download_url = response.json()["assets"][0]["browser_download_url"]
    # Compare and prompt user to download
```

---

## Summary

### Recommended Approach for Different Scenarios

| Scenario | Recommended Method | Why |
|----------|-------------------|-----|
| Small team (< 10 users) | Simple launcher | Easy to update, no build needed |
| Medium org (10-100 users) | Portable ZIP | No installation, easy deployment |
| Public release | Professional installer | Most user-friendly |
| Technical users | GitHub repository | They can build themselves |
| Non-technical users | Installer + Video tutorial | Holds their hand through setup |

### Quick Distribution Workflow

1. **Build** all versions using `build_installer.py`
2. **Test** on clean machines (all platforms)
3. **Package** with documentation
4. **Upload** to distribution platform
5. **Share** link with clear instructions
6. **Support** users via email/issues

### Next Steps

1. Choose your distribution method
2. Build the installers
3. Test thoroughly
4. Create user documentation
5. Set up support channel
6. Distribute to users!

---

**Questions? Issues?**

- Check TROUBLESHOOTING.txt
- Review FAQ section
- Contact support

Happy distributing! 🚀
