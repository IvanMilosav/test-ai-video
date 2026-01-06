# Iterative Clip Ontology Builder

A system for analyzing YouTube video ads and building a comprehensive, vertical-agnostic clip selection ontology.

## How It Works

1. **First video**: The system analyzes the video and creates an initial ontology with all discovered clip attributes, emotions, functions, etc.

2. **Subsequent videos**: Each new video is analyzed with knowledge of the existing ontology. The system:
   - Uses known values to guide consistent categorization
   - Discovers new values and adds them to the ontology
   - Tracks frequency of each value to understand what's common
   - Builds correlations (e.g., which emotions pair with which functions)

3. **Output per video**: Each video produces a text file showing every clip with its full ontology annotation, including the exact script segment for that clip.

4. **Master ontology**: A JSON file that grows with each video, containing all discovered categories, values, and patterns.

## Files

- `clip_ontology_schema.py` - Defines the clip ontology structure
- `iterative_analyzer.py` - Core analysis engine using Gemini
- `batch_processor.py` - Processes directories of videos
- `ontology_reporter.py` - Generates reports from the ontology

## Usage

### Process a single video
```bash
python iterative_analyzer.py video.mp4
```

### Process a directory of videos
```bash
# Process all videos in a directory
python batch_processor.py /path/to/videos

# Specify output directory
python batch_processor.py /path/to/videos --output ./results

# Use faster model
python batch_processor.py /path/to/videos --model flash

# Process only first N videos
python batch_processor.py /path/to/videos --limit 5
```

### View ontology status
```bash
# Show current ontology report
python batch_processor.py --status

# Generate full report
python ontology_reporter.py master_clip_ontology.json

# Export as JSON
python ontology_reporter.py master_clip_ontology.json --format json
```

## Output Format

Each video produces a `.txt` file with this structure:

```
═══════════════════════════════════════════════════════════════
VIDEO CLIP ONTOLOGY ANALYSIS
═══════════════════════════════════════════════════════════════
Video: example_ad.mp4
Analyzed: 2024-01-15 10:30:00
Total Clips: 24

═══════════════════════════════════════════════════════════════
FULL TRANSCRIPT
═══════════════════════════════════════════════════════════════
[Complete verbatim transcript of all spoken words]

═══════════════════════════════════════════════════════════════
CLIP-BY-CLIP ONTOLOGY
═══════════════════════════════════════════════════════════════

──────────────────────────────────────────────────────────────
CLIP 1
Timestamp: 00:00.000 → 00:02.500 (2.50s)
──────────────────────────────────────────────────────────────

SCRIPT SEGMENT:
  "Ever wonder why your competitors are crushing it?"

VISUAL ONTOLOGY:
  Shot Type: medium_close_up
  Camera: eye_level angle, static movement
  Composition: centered
  Setting: studio - Professional studio with neutral background
  Lighting: studio
  Color Mood: warm (orange, cream)
  Subject: person (1) - speaking
  Subject Detail: Male host in casual business attire

AUDIO ONTOLOGY:
  Speaker: host (visible: True)
  Vocal Delivery: conversational tone, moderate pacing, medium energy
  Emphasis Words: wonder, crushing
  Music: subtle - corporate (low energy)

EMOTIONAL ONTOLOGY:
  Primary Emotion: curiosity
  Intensity: moderate
  Direction: transitioning

FUNCTIONAL ONTOLOGY:
  Clip Function: hook
  Narrative Role: setup
  Persuasion Mechanism: curiosity_gap
  Persuasion Target: attention

STRUCTURAL ONTOLOGY:
  Transition In: fade_in
  Transition Out: cut
  Sets Up Next: Establishes question that body will answer

PURPOSE:
  Opens with relatable question to create curiosity gap and capture attention in first 2 seconds.

[... continues for each clip ...]
```

## Ontology Categories

The system tracks these categories (which expand with each video):

### Visual
- Shot types (close_up, medium, wide, etc.)
- Camera angles (eye_level, high_angle, etc.)
- Camera movements (static, pan, zoom, etc.)
- Compositions (rule_of_thirds, centered, etc.)
- Setting types (studio, outdoor, screen_recording, etc.)
- Lighting styles (natural, dramatic, high_key, etc.)
- Color moods (warm, cool, vibrant, etc.)
- Subject types (person, product, text_screen, etc.)
- Subject actions (speaking, demonstrating, etc.)

### Audio
- Speaker types (host, voiceover, testimonial, etc.)
- Vocal tones (excited, calm, urgent, etc.)
- Vocal pacing (slow, moderate, fast, etc.)
- Music styles (upbeat, dramatic, corporate, etc.)

### Emotional
- Emotions (curiosity, fear, desire, trust, etc.)
- Emotional intensities (subtle, moderate, strong, etc.)

### Functional
- Clip functions (hook, problem, solution, demo, cta, etc.)
- Narrative roles (setup, build, payoff, etc.)
- Persuasion mechanisms (curiosity_gap, social_proof, scarcity, etc.)

### Structural
- Transition types (cut, dissolve, fade, etc.)

## Requirements

```bash
pip install google-genai
export GOOGLE_API_KEY='your-api-key'
```

## Tips

1. **Start with diverse videos**: The ontology learns better from varied content
2. **Use `--model pro`** for best accuracy on first videos to establish solid foundation
3. **Switch to `--model flash`** once ontology is established for faster processing
4. **Check the report** periodically with `--status` to see what's been discovered
