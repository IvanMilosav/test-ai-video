# Video Analyzer - Quick Installation Guide

## For End Users (Non-Technical)

### Linux Installation

**One-Command Setup:**
```bash
./install_launcher.sh
```

That's it! This will:
- ✓ Check if Python is installed
- ✓ Generate the application icon
- ✓ Create a desktop shortcut
- ✓ Set up everything automatically

**After installation:**
1. Look for the **VideoAnalyzer** icon on your desktop
2. Double-click it to launch
3. If you see "Untrusted Application" warning, click **Allow Launching**

---

### Windows Installation

**Double-click:** `video_analyzer.bat`

**To create desktop shortcut:**
1. Right-click `video_analyzer.bat`
2. Select **Send to → Desktop (create shortcut)**
3. Double-click the desktop shortcut to launch

---

### macOS Installation

**Option 1 - Quick Launch (Recommended):**
```bash
chmod +x video_analyzer.sh
./video_analyzer.sh
```

**Option 2 - Create Application:**
1. Open **Automator**
2. Choose **Application**
3. Add **Run Shell Script** action
4. Paste this (update the path):
   ```bash
   cd "/path/to/advisualbreakdown"
   ./video_analyzer.sh
   ```
5. Save as **Video Analyzer.app** in Applications folder

---

## Requirements

- **Python 3.8+** (most systems have this by default)
- **tkinter** (GUI library)
- **Google Gemini API key** (get free at [ai.google.dev](https://ai.google.dev))

### Installing Python & Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-tk python3-pip
pip3 install google-generativeai pillow
```

**Fedora:**
```bash
sudo dnf install python3 python3-tkinter python3-pip
pip3 install google-generativeai pillow
```

**macOS:**
```bash
# Install Homebrew first if needed: https://brew.sh
brew install python-tk
pip3 install google-generativeai pillow
```

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. During installation, check **"Add Python to PATH"**
3. Open Command Prompt and run:
   ```
   pip install google-generativeai pillow
   ```

---

## Troubleshooting

### "Permission denied"
**Linux/Mac:**
```bash
chmod +x video_analyzer.sh
chmod +x install_launcher.sh
```

### "Python not found"
Make sure Python 3 is installed:
```bash
python3 --version
```

### "No module named 'tkinter'"
**Ubuntu/Debian:**
```bash
sudo apt install python3-tk
```

**Fedora:**
```bash
sudo dnf install python3-tkinter
```

**macOS:**
```bash
brew install python-tk
```

### "Cannot open desktop file" or "Untrusted application"
Right-click the desktop icon and select:
- **Ubuntu/GNOME:** Allow Launching
- **Fedora:** Trust this application
- **KDE:** Mark as Executable

Or via command:
```bash
gio set ~/Desktop/VideoAnalyzer.desktop metadata::trusted true
```

### Need more help?
- Check: `FIX_DESKTOP_LAUNCHER.md` for detailed Linux fixes
- Check: `QUICK_LAUNCHER_SETUP.txt` for platform-specific guides

---

## Creating Standalone Executable (No Python needed)

Want to share with users who don't have Python? Create a standalone app:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name "Video Analyzer" \
  --icon=icon.ico video_analyzer_gui.py

# Find it in: dist/Video Analyzer
```

The executable in `dist/` folder can be shared with anyone!

---

## First Run

1. **Launch the application**
2. **Enter your Gemini API key** in Settings
3. **Select a video file** to analyze
4. **Choose analysis type:**
   - **Ontology Analysis:** Learn patterns and statistics
   - **Script-Clip Brain:** Match script to video clips
5. **Start Analysis** and watch it learn!

---

## Features

- 🎥 **AI Video Analysis** using Google Gemini Vision
- 🧠 **Iterative Learning** - Gets smarter with each video
- 📊 **Master Ontology** - Tracks patterns and statistics
- 📝 **Script-Clip Brain** - Creates playbook for editing
- 👁️ **View Data** - Explore all learned patterns via GUI menus

---

## For General Distribution

If you're sharing this with non-technical users:

1. **Run the installer** to verify everything works
2. **Create PyInstaller executable** for their platform
3. **Include icon files** (already generated)
4. **Provide this README** for setup instructions

The PyInstaller executable is the best option - users just double-click and it runs without Python installation!

---

**Made for general usage - just click and analyze! 🚀**
