# GUI Update - Data Viewer Features

## New Features Added ✨

The Video Analyzer GUI now includes built-in data viewers to explore all your learned video patterns!

### Menu Bar Added

Two new menus at the top of the window:

#### **"View Data" Menu**
- 📊 **Master Ontology (Statistics)** - View overall patterns from all videos
- 🧠 **Script-Clip Brain (Recipes)** - Browse real script-to-clip examples
- 🎬 **Recent Video Analyses** - View clip-by-clip breakdowns of analyzed videos
- 📖 **Help Guide** - Complete guide to understanding your data

#### **"File" Menu**
- Open Video... - Browse for video files
- Open Output Folder - Quick access to output directory
- Exit - Close the application

---

## Feature Details

### 1. Master Ontology Viewer
**Access**: View Data → Master Ontology (Statistics)

**Shows**:
- Total videos and clips analyzed
- All visual patterns (shot types, camera angles, lighting, colors, etc.)
- Emotional patterns (which emotions are common)
- Functional patterns (hook, problem, solution frequencies)
- Duration averages by function
- Emotion-function correlations

**Use Case**: "How long should my problem clips be?" → See average durations

### 2. Script-Clip Brain Viewer
**Access**: View Data → Script-Clip Brain (Recipes)

**Shows**:
- 160+ real examples organized by clip type
- Examples organized by function (hook, problem, solution, etc.)
- Transition patterns (what follows what)
- Quick reference rules

**Use Case**: "When script mentions the product, what should I show?" → Find similar examples

### 3. Recent Video Analyses
**Access**: View Data → Recent Video Analyses

**Shows**:
- List of all analyzed videos (sorted by date)
- File size and analysis date
- Double-click or select to view full clip-by-clip breakdown

**Features**:
- Shows all 83+ clips from a video
- Complete visual, emotional, and functional data for each clip
- Full transcript
- Timestamps for every clip

**Use Case**: "How did the Gabriel ad structure work?" → View complete breakdown

### 4. Help Guide
**Access**: View Data → Help Guide

**Shows**:
- Complete guide to all data files
- Practical use case examples
- Where to find specific information

---

## Viewer Features

All data viewers include:

✅ **Search Functionality**
- Type a search term and press Enter or click "Find"
- Highlights all occurrences
- Jump to first match automatically

✅ **Read-Only View**
- Safe browsing - can't accidentally edit data
- Monospace font for easy reading
- Syntax highlighting for search results

✅ **File Information**
- Shows file size and line count
- Displays file name

✅ **Quick Actions**
- "Open in Editor" button - opens file in your default text editor
- "Close" button - closes the viewer

✅ **Scrollable Content**
- Vertical and horizontal scrollbars
- Navigate large files easily

---

## How to Use

### Start the GUI:
```bash
python video_analyzer_gui.py
```

### View Master Statistics:
1. Click **View Data** menu
2. Select **Master Ontology (Statistics)**
3. Browse patterns learned from all videos
4. Search for specific terms (e.g., "problem", "fear", "duration")

### Find Recipe Examples:
1. Click **View Data** menu
2. Select **Script-Clip Brain (Recipes)**
3. Browse by clip type or function
4. Search for script phrases similar to yours

### Study a Specific Video:
1. Click **View Data** menu
2. Select **Recent Video Analyses**
3. Double-click a video from the list
4. Study clip-by-clip breakdown with timestamps

---

## Screenshots

### Main Window with Menu
```
┌─────────────────────────────────────────────┐
│ File    View Data                           │
├─────────────────────────────────────────────┤
│                                             │
│           🎬 Video Analyzer                 │
│          Powered by Gemini AI               │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │         📁                             │ │
│  │  Click to Select Video File            │ │
│  │   (or drag & drop here)                │ │
│  │   [Browse Files]                       │ │
│  └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

### Data Viewer Window
```
┌─────────────────────────────────────────────┐
│ Master Ontology - Statistics Brain          │
├─────────────────────────────────────────────┤
│ Overall patterns learned from ALL videos    │
│ 📄 master_clip_ontology.txt | 5.6KB        │
│                                             │
│ Search: [________________] [Find]           │
│                                             │
│ ┌─────────────────────────────────────────┐│
│ │ ======================================  ││
│ │ MASTER CLIP ONTOLOGY                    ││
│ │ ======================================  ││
│ │ Videos Analyzed: 4                      ││
│ │ Total Clips: 340                        ││
│ │                                         ││
│ │ Shot Types:                             ││
│ │   close_up (168x)                       ││
│ │   medium (126x)                         ││
│ │   ...                                   ││
│ └─────────────────────────────────────────┘│
│                                             │
│    [Open in Editor]  [Close]                │
└─────────────────────────────────────────────┘
```

---

## Tips

1. **Use Search** - All viewers have search. Great for finding specific terms quickly.

2. **Open in Editor** - If you want to copy-paste or analyze in detail, click "Open in Editor"

3. **Multiple Windows** - You can open multiple viewers at once to compare data

4. **Recent First** - Video analyses are sorted newest first for easy access

5. **Pattern Discovery** - Use Master Ontology to discover what makes successful ads work

---

## Requirements

No new dependencies needed! Uses built-in tkinter components.

---

## Next Steps

After viewing the data:
1. Use patterns to plan your next video
2. Reference the brain for clip selection
3. Study successful video structures
4. Apply learned correlations to your content

Happy analyzing! 🎬
