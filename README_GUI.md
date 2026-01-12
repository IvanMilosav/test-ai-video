# Video Analyzer GUI

A cross-platform desktop application for analyzing videos using Google's Gemini AI.

## 🌍 Cross-Platform Support

Works on:
- ✅ **Windows** 10/11
- ✅ **macOS** (10.14+)
- ✅ **Linux** (Ubuntu, Fedora, Debian, etc.)

## 📋 Requirements

- Python 3.8 or higher
- Gemini API key (Google AI)

## 🚀 Quick Start

### 1. Install Dependencies

**All Platforms:**
```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project directory:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Run the Application

**Windows:**
```bash
python video_analyzer_gui.py
```
Or double-click: `start_gui.bat`

**macOS/Linux:**
```bash
python3 video_analyzer_gui.py
```
Or make executable and run:
```bash
chmod +x start_gui.sh
./start_gui.sh
```

## 💡 How to Use

1. **Launch the application** - Run the program using one of the methods above
2. **Click "Browse Files"** - Select your video file (MP4, MOV, AVI, MKV)
3. **Click "Analyze Video"** - Processing begins automatically
4. **View Progress** - Real-time progress bar and status updates
5. **Get Results** - Output file is generated with option to open folder

## 📁 Supported Formats

- **Video:** MP4, MOV, AVI, MKV
- **Max Size:** 20MB (use compress tool for larger files)

## 🎯 Features

- ✅ Modern dark theme UI
- ✅ Drag-and-drop support (where available)
- ✅ Real-time progress tracking
- ✅ Automatic output file generation
- ✅ Option to open results folder
- ✅ Error handling with helpful messages
- ✅ Multi-threaded processing (UI stays responsive)

## 🔧 Compressing Large Videos

If your video is over 20MB, use the compression tool first:

```bash
python compress_videos.py your_video.mp4
```

This creates a compressed version optimized for Gemini analysis.

## 📤 Output

Analysis results are saved as `.txt` files in the same directory with:
- Complete video transcription
- Clip-by-clip breakdown
- Visual and audio analysis
- Emotional and engagement metrics
- Timestamps and detailed ontology

## ⚙️ Platform-Specific Notes

### Windows
- Full drag-and-drop support
- Uses native file dialogs
- Opens output folder with Explorer

### macOS
- Tkinter comes with Python
- Uses native macOS file picker
- Opens output folder with Finder
- Drag-and-drop may vary by macOS version

### Linux
- Tkinter usually pre-installed with Python
- If missing, install: `sudo apt install python3-tk` (Ubuntu/Debian)
- Opens output folder with default file manager
- Drag-and-drop support varies by desktop environment

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
- Create a `.env` file with your API key
- Make sure it's in the same directory as the scripts

### "tkinter not found" (Linux)
```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch
sudo pacman -S tk
```

### Drag-and-drop not working
- Use the **Browse Files** button instead (always works)
- Drag-and-drop is a bonus feature, not required

### Video opens instead of loading (Windows)
- Use the Browse Files button
- The button is the recommended method

## 📝 Command Line Alternative

Prefer command line? Use:
```bash
python analyze_video.py your_video.mp4
```

## 🔐 Privacy & Security

- All processing is done via Google's Gemini API
- Videos are sent to Google for analysis
- No local storage of video data
- API key is loaded from local `.env` file

## 📄 License

This tool uses the Gemini API which requires a Google AI API key.

## 🤝 Support

For issues, check:
1. API key is correctly set in `.env`
2. Video is under 20MB
3. Python dependencies are installed
4. Video format is supported

---

**Made with Gemini AI** 🤖