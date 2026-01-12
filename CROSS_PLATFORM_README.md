# 🎬 Video Analyzer - Cross-Platform Edition

**AI-powered video analysis tool that works on Linux, macOS, and Windows**

---

## ⚡ Quick Start

### 🐧 Linux
```bash
./start_video_analyzer.sh
# Or use Applications Menu: Super → "Video Analyzer"
```

### 🍎 macOS
```bash
./setup_macos.sh    # First time only
./start_mac.sh      # Launch app
```

### 🪟 Windows
```cmd
start_gui.bat
```

---

## 📚 Platform-Specific Guides

- **Linux Users**: Main README + Desktop icon already configured
- **macOS Users**: See [MACOS_SETUP.md](MACOS_SETUP.md)
- **All Platforms**: See [PLATFORM_GUIDE.md](PLATFORM_GUIDE.md)

---

## 🚀 Available Launchers

| Launcher | Platform | Description |
|----------|----------|-------------|
| `start_video_analyzer.sh` | **All** | Auto-detects OS and launches |
| `video_analyzer_fixed.sh` | Linux | Full-featured Linux launcher |
| `start_mac.sh` | macOS | macOS-optimized launcher |
| `start_gui.sh` | Linux/Mac | Simple launcher |
| `start_gui.bat` | Windows | Windows batch launcher |
| `run-video-analyzer` | Linux/Mac | Minimal launcher |
| `desktop_launcher.sh` | Linux | Desktop icon wrapper |

---

## 📦 Installation

### All Platforms: Common Steps

1. **Install Python 3.8+**
   - Linux: `sudo apt install python3 python3-pip python3-venv`
   - macOS: Download from python.org or `brew install python3`
   - Windows: Download from python.org

2. **Create Virtual Environment**
   ```bash
   # Linux/macOS
   python3 -m venv venv

   # Windows
   python -m venv venv
   ```

3. **Install Dependencies**
   ```bash
   # Linux/macOS
   ./venv/bin/pip install -r requirements.txt

   # Windows
   venv\Scripts\pip install -r requirements.txt
   ```

4. **Configure API Key**
   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

5. **Launch!**
   - See Quick Start section above

---

## 🎯 Platform-Specific Features

### Linux Features
✅ Desktop icon (.desktop file)
✅ Applications menu integration
✅ zenity/kdialog dialogs
✅ Native file manager integration

### macOS Features
✅ AppleScript dialogs (osascript)
✅ Automator .app bundle support
✅ Native Finder integration
✅ Menu bar integration

### Windows Features
✅ Batch file launchers
✅ Desktop shortcut support
✅ Windows Explorer integration
✅ Optional .exe creation (PyInstaller)

---

## 🔧 Key Differences by Platform

### Python & tkinter

**Linux:**
- Install separately: `sudo apt install python3-tk`
- Package manager: apt/dnf/pacman

**macOS:**
- Included in python.org installer ✅
- Separate with Homebrew: `brew install python-tk`

**Windows:**
- Included in standard Python installer ✅
- No extra steps needed

### Dialogs

**Linux:**
```bash
zenity --info --text="Message"
kdialog --msgbox "Message"
```

**macOS:**
```bash
osascript -e 'display dialog "Message"'
```

**Windows:**
```python
import tkinter.messagebox
tkinter.messagebox.showinfo("Title", "Message")
```

---

## 📝 File Overview

### Launchers
- `start_video_analyzer.sh` - Universal launcher (recommended)
- `start_mac.sh` - macOS-specific with AppleScript dialogs
- `video_analyzer_fixed.sh` - Linux-specific with proper error handling
- `start_gui.bat` - Windows batch file

### Setup Scripts
- `setup_macos.sh` - macOS one-time setup
- `fix_desktop_permissions.sh` - Linux desktop icon helper
- `install_launcher.sh` - Linux system integration

### Documentation
- `PLATFORM_GUIDE.md` - Cross-platform overview
- `MACOS_SETUP.md` - Detailed macOS guide
- `QUICK_START.txt` - Quick reference
- `HOW_TO_LAUNCH.md` - All launch methods

---

## 🆘 Common Issues

### "Permission denied"
```bash
# Linux/macOS
chmod +x *.sh

# Windows
# Right-click → Properties → Unblock
```

### "tkinter not found"
```bash
# Linux
sudo apt-get install python3-tk

# macOS (Homebrew)
brew install python-tk@3.12

# Windows
# Reinstall Python with tkinter option checked
```

### "Module not found"
```bash
# Reinstall dependencies
./venv/bin/pip install -r requirements.txt  # Linux/Mac
venv\Scripts\pip install -r requirements.txt  # Windows
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Then recreate
python3 -m venv venv  # Linux/Mac
python -m venv venv  # Windows
```

---

## 🎨 Creating Native Launchers

### Linux: Desktop Icon
Already included! Just right-click `VideoAnalyzer.desktop` → "Allow Launching"

### macOS: App Bundle
1. Open **Automator**
2. Create **Application**
3. Add **Run Shell Script**:
   ```bash
   cd "/path/to/advisualbreakdown"
   ./start_mac.sh
   ```
4. Save as `Video Analyzer.app`

### Windows: Desktop Shortcut
1. Right-click `start_gui.bat`
2. Send to → Desktop (create shortcut)
3. (Optional) Right-click shortcut → Properties → Change Icon

---

## ✅ Verification

Test your installation:

```bash
# Check Python
python3 --version  # or: python --version

# Check tkinter
python3 -c "import tkinter; print('✅ tkinter OK')"

# Check virtual environment
ls venv/  # Should see bin/ (Linux/Mac) or Scripts/ (Windows)

# Check dependencies
./venv/bin/pip list  # Linux/Mac
venv\Scripts\pip list  # Windows

# Run verification script (Linux only)
./verify_setup.sh
```

---

## 📊 Platform Support Matrix

| Feature | Linux | macOS | Windows |
|---------|:-----:|:-----:|:-------:|
| **GUI Application** | ✅ | ✅ | ✅ |
| **Drag & Drop** | ✅ | ✅ | ✅ |
| **Virtual Environment** | ✅ | ✅ | ✅ |
| **Desktop Icon** | ✅ | ⚠️* | ✅ |
| **System Menu** | ✅ | ⚠️* | ❌ |
| **Shell Scripts** | ✅ | ✅ | ⚠️** |
| **Batch Files** | ❌ | ❌ | ✅ |
| **Native Dialogs** | ✅ | ✅ | ✅ |

*macOS uses .app bundles instead of .desktop files
**Windows requires Git Bash for .sh files, or use .bat files

---

## 🌐 Getting Started by Platform

### I'm on Linux
1. ✅ Everything is already set up!
2. Use Applications Menu: Super → "Video Analyzer"
3. Or: `./start_video_analyzer.sh`

### I'm on macOS
1. Run: `./setup_macos.sh` (one time)
2. Launch: `./start_mac.sh`
3. Read: [MACOS_SETUP.md](MACOS_SETUP.md)

### I'm on Windows
1. Create venv: `python -m venv venv`
2. Install: `venv\Scripts\pip install -r requirements.txt`
3. Launch: `start_gui.bat`

---

## 🎯 Recommendations

**For easiest cross-platform compatibility:**
1. Use `start_video_analyzer.sh` - auto-detects OS
2. Keep virtual environment in project folder
3. Use relative paths in scripts
4. Test on your target platform

**For best native experience:**
- **Linux**: Use Applications Menu
- **macOS**: Create Automator .app
- **Windows**: Create Desktop shortcut

---

## 📄 License & Credits

Video Analyzer - AI-powered video analysis
Built with Python, tkinter, and Google Gemini API

---

**Your Video Analyzer is now fully cross-platform!** 🎉

Choose your platform above and start analyzing videos!
