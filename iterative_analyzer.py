"""
Iterative Clip Ontology Analyzer
=================================
Processes videos one at a time, building and refining the ontology with each video.
The ontology becomes more comprehensive and vertical-agnostic over time.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from config import Config
from clip_ontology_schema import (
    ClipOntology,
    MasterClipOntology,
    AnnotatedClip,
    OntologyCategory
)
from script_clip_brain import ScriptClipBrain


class IterativeClipAnalyzer:
    """
    Analyzes videos iteratively, building a universal clip ontology.
    Each video refines and expands the ontology.
    """

    MODELS = {
        "pro": "gemini-3-pro-preview",
        "flash": "gemini-2.0-flash",
    }

    def __init__(
        self,
        api_key: str = None,
        model: str = "pro",
        ontology_path: str = "master_clip_ontology.pkl",
        brain_path: str = "script_clip_brain.pkl",
        progress_callback: callable = None
    ):
        # Use Config for API key, with optional override
        self.api_key = api_key or Config.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY required - set in config.py or .env")

        self.client = genai.Client(api_key=self.api_key)
        self.model = self.MODELS.get(model, "gemini-2.0-pro")
        self.ontology_path = ontology_path
        self.brain_path = brain_path
        self.progress_callback = progress_callback

        # Load or create master ontology (from pickle)
        if os.path.exists(ontology_path):
            self.master_ontology = MasterClipOntology.load_binary(ontology_path)
            print(f"Loaded ontology: {self.master_ontology.videos_analyzed} videos, "
                  f"{self.master_ontology.total_clips_analyzed} clips")
        else:
            self.master_ontology = MasterClipOntology()
            print("Created new master ontology")

        # Load or create brain
        self.brain = ScriptClipBrain.load(brain_path)
        print(f"Loaded brain: {self.brain.videos_learned_from} videos learned")

    def _build_analysis_prompt(self) -> str:
        """
        Build the analysis prompt - VISUAL, EMOTIONAL, FUNCTIONAL only.
        """
        known_values = self._get_known_ontology_values()

        prompt = f'''You are an expert video editor analyzing a video advertisement. Identify EVERY SINGLE CLIP CHANGE and describe each using VISUAL, EMOTIONAL, and FUNCTIONAL ontology.

## CLIP DETECTION

A new clip starts when ANY of these occur:
- Camera angle/position/movement changes
- Scene or location changes
- Subject changes or significant movement
- Shot type changes (wide to close-up, etc.)
- B-roll or cutaway insertions
- Graphics/text appear/change/disappear
- Screen recordings or demos start/stop
- Any visual discontinuity

## KNOWN ONTOLOGY VALUES

{known_values}

## OUTPUT FORMAT - JSON

{{
  "video_summary": {{
    "total_duration_seconds": <float>,
    "total_clips": <integer>,
    "full_transcript": "<complete verbatim transcript>"
  }},
  "clips": [
    {{
      "clip_number": <int>,
      "timestamp_start": "<MM:SS.mmm>",
      "timestamp_end": "<MM:SS.mmm>",
      "duration_seconds": <float>,
      "script_segment": "<EXACT words spoken in THIS clip>",

      "visual": {{
        "shot_type": "<close_up|medium|wide|extreme_close_up|insert|overhead>",
        "camera_angle": "<eye_level|high_angle|low_angle|dutch|birds_eye>",
        "camera_movement": "<static|pan|tilt|zoom_in|zoom_out|tracking|handheld>",
        "composition": "<centered|rule_of_thirds|symmetrical|dynamic>",
        "setting_type": "<indoor|outdoor|studio|screen_recording|animated>",
        "setting_description": "<description>",
        "lighting_style": "<natural|studio|dramatic|soft|high_key|low_key>",
        "color_mood": "<warm|cool|neutral|vibrant|muted>",
        "subject_type": "<person|product|text_screen|graphic|b_roll>",
        "subject_description": "<who/what>",
        "subject_action": "<speaking|demonstrating|reacting|gesturing|static>",
        "text_on_screen": ["<text line 1>"],
        "text_purpose": "<headline|subtitle|cta|statistic|quote|none>"
      }},

      "emotional": {{
        "primary_emotion": "<curiosity|fear|desire|trust|excitement|frustration|hope|urgency>",
        "secondary_emotion": "<optional>",
        "emotional_intensity": "<subtle|moderate|strong>",
        "emotional_direction": "<positive|negative|neutral|transitioning>"
      }},

      "functional": {{
        "clip_function": "<hook|problem|agitation|solution|demo|benefit|proof|cta|transition>",
        "narrative_role": "<setup|build|escalate|pivot|payoff|reinforce>",
        "persuasion_mechanism": "<curiosity_gap|pain_agitation|social_proof|authority|scarcity|demonstration>",
        "persuasion_target": "<belief|emotion|action|awareness>"
      }},

      "transition_in": "<cut|dissolve|fade|wipe|zoom>",
      "transition_out": "<cut|dissolve|fade|wipe|zoom>",
      "purpose_summary": "<WHY this clip exists here>"
    }}
  ]
}}

## REQUIREMENTS

1. Catch EVERY clip - no gaps, no overlaps
2. script_segment = EXACT verbatim words for THAT clip only
3. Timestamps: MM:SS.mmm format, end of clip N = start of clip N+1
4. purpose_summary explains WHY, not just what

OUTPUT ONLY VALID JSON.'''

        return prompt

    def _get_known_ontology_values(self) -> str:
        """Get formatted string of known ontology values."""
        if self.master_ontology.total_clips_analyzed == 0:
            return "First analysis - discover all values."

        lines = []
        o = self.master_ontology

        categories = [
            ("Shot Types", o.shot_types),
            ("Camera Angles", o.camera_angles),
            ("Camera Movements", o.camera_movements),
            ("Setting Types", o.setting_types),
            ("Lighting Styles", o.lighting_styles),
            ("Color Moods", o.color_moods),
            ("Subject Types", o.subject_types),
            ("Subject Actions", o.subject_actions),
            ("Emotions", o.emotions),
            ("Clip Functions", o.clip_functions),
            ("Narrative Roles", o.narrative_roles),
            ("Persuasion Mechanisms", o.persuasion_mechanisms),
        ]

        for name, cat in categories:
            if cat.values:
                vals = cat.get_top_values(10)
                lines.append(f"{name}: {', '.join(vals)}")

        return "\n".join(lines) if lines else "First analysis - discover all values."

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        """Analyze a single video and return structured clip data."""
        print(f"\n{'='*60}")
        print(f"ANALYZING VIDEO")
        print(f"{'='*60}")
        print(f"File: {video_path}")
        print(f"Model: {self.model}")
        print(f"Current ontology: {self.master_ontology.total_clips_analyzed} clips from "
              f"{self.master_ontology.videos_analyzed} videos")

        # Validate
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        print(f"File size: {file_size_mb:.2f} MB")

        if file_size_mb > 200:
            raise ValueError(f"File too large: {file_size_mb:.2f} MB (max 200MB)")

        # Load video
        with open(video_path, 'rb') as f:
            video_bytes = f.read()

        ext = os.path.splitext(video_path)[1].lower()
        mime_types = {'.mp4': 'video/mp4', '.mov': 'video/quicktime', '.webm': 'video/webm'}
        mime_type = mime_types.get(ext, 'video/mp4')

        # Build prompt with current ontology knowledge
        prompt = self._build_analysis_prompt()

        # Send to Gemini
        print("Sending to Gemini for analysis...")
        contents = [types.Content(
            role="user",
            parts=[
                types.Part.from_bytes(mime_type=mime_type, data=video_bytes),
                types.Part.from_text(text=prompt)
            ]
        )]

        response_text = ""
        chunk_count = 0
        try:
            response_stream = self.client.models.generate_content_stream(
                model=self.model,
                contents=contents
            )
            print("Receiving response from Gemini...")
            for chunk in response_stream:
                if chunk.text:
                    response_text += chunk.text
                    chunk_count += 1
                    # Print progress every 10 chunks
                    if chunk_count % 10 == 0:
                        print(f"  Received {len(response_text)} characters so far...")
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

        print(f"Received complete response: {len(response_text)} chars from {chunk_count} chunks")

        # Parse response
        analysis = self._parse_response(response_text)

        return analysis

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response with error handling."""
        clean = response_text.strip()

        # Remove markdown
        if clean.startswith('```json'):
            clean = clean[7:]
        elif clean.startswith('```'):
            clean = clean[3:]
        if clean.endswith('```'):
            clean = clean[:-3]

        try:
            return json.loads(clean.strip())
        except json.JSONDecodeError:
            pass

        # Find JSON block
        start = response_text.find('{')
        if start == -1:
            raise ValueError("No JSON found in response")

        brace_count = 0
        for i in range(start, len(response_text)):
            if response_text[i] == '{':
                brace_count += 1
            elif response_text[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    try:
                        return json.loads(response_text[start:i+1])
                    except json.JSONDecodeError as e:
                        raise ValueError(f"JSON parse error: {e}")

        raise ValueError("Could not parse JSON")

    def _convert_to_clip_ontology(self, clip_data: Dict[str, Any]) -> ClipOntology:
        """Convert raw clip data to ClipOntology object."""
        visual = clip_data.get('visual', {})
        emotional = clip_data.get('emotional', {})
        functional = clip_data.get('functional', {})

        return ClipOntology(
            timestamp_start=clip_data.get('timestamp_start', ''),
            timestamp_end=clip_data.get('timestamp_end', ''),
            duration_seconds=clip_data.get('duration_seconds', 0),

            # Script
            script_segment=clip_data.get('script_segment', ''),

            # Visual
            shot_type=visual.get('shot_type', ''),
            camera_angle=visual.get('camera_angle', ''),
            camera_movement=visual.get('camera_movement', ''),
            composition=visual.get('composition', ''),
            setting_type=visual.get('setting_type', ''),
            setting_description=visual.get('setting_description', ''),
            lighting_style=visual.get('lighting_style', ''),
            color_mood=visual.get('color_mood', ''),
            subject_type=visual.get('subject_type', ''),
            subject_description=visual.get('subject_description', ''),
            subject_action=visual.get('subject_action', ''),
            text_on_screen=visual.get('text_on_screen', []),
            text_purpose=visual.get('text_purpose', ''),

            # Emotional
            primary_emotion=emotional.get('primary_emotion', ''),
            secondary_emotion=emotional.get('secondary_emotion', ''),
            emotional_intensity=emotional.get('emotional_intensity', ''),
            emotional_direction=emotional.get('emotional_direction', ''),

            # Functional
            clip_function=functional.get('clip_function', ''),
            narrative_role=functional.get('narrative_role', ''),
            persuasion_mechanism=functional.get('persuasion_mechanism', ''),
            persuasion_target=functional.get('persuasion_target', ''),

            # Structure
            transition_in=clip_data.get('transition_in', ''),
            transition_out=clip_data.get('transition_out', ''),

            purpose_summary=clip_data.get('purpose_summary', '')
        )

    def update_ontology(self, analysis: Dict[str, Any]) -> List[AnnotatedClip]:
        """Update master ontology and brain with analysis results."""
        clips = analysis.get('clips', [])
        annotated_clips = []

        print(f"\nUpdating ontology with {len(clips)} clips...")

        for clip_data in clips:
            clip_ontology = self._convert_to_clip_ontology(clip_data)
            self.master_ontology.update_from_clip(clip_ontology)

            annotated = AnnotatedClip(
                clip_number=clip_data.get('clip_number', 0),
                ontology=clip_ontology
            )
            annotated_clips.append(annotated)

            # Train the brain on this clip
            self.brain.learn_from_clip(clip_data)

        # Track sequence pattern
        sequence = [c.ontology.clip_function for c in annotated_clips if c.ontology.clip_function]
        if sequence:
            self.master_ontology.common_sequences.append(sequence)

        # Train brain on sequence patterns
        self.brain.learn_sequence(clips)

        # Increment counts and save
        self.master_ontology.videos_analyzed += 1
        self.brain.videos_learned_from += 1

        self.master_ontology.save(self.ontology_path)
        self.brain.save(self.brain_path)

        print(f"Ontology updated: now {self.master_ontology.total_clips_analyzed} total clips "
              f"from {self.master_ontology.videos_analyzed} videos")
        print(f"Brain updated: learned from {self.brain.videos_learned_from} videos")

        return annotated_clips

    def generate_output(
        self,
        video_path: str,
        analysis: Dict[str, Any],
        annotated_clips: List[AnnotatedClip],
        output_dir: str = None
    ) -> str:
        """Generate text output file only."""
        if output_dir is None:
            output_dir = os.path.dirname(video_path) or '.'

        base_name = os.path.splitext(os.path.basename(video_path))[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        text_path = os.path.join(output_dir, f"{base_name}_ontology_{timestamp}.txt")

        # Generate text output
        lines = []
        lines.append("=" * 70)
        lines.append("VIDEO CLIP ONTOLOGY ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"Video: {os.path.basename(video_path)}")
        lines.append(f"Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Clips: {len(annotated_clips)}")

        summary = analysis.get('video_summary', {})
        lines.append(f"Duration: {summary.get('total_duration_seconds', 'N/A')} seconds")
        lines.append("")

        # Full transcript
        lines.append("=" * 70)
        lines.append("FULL TRANSCRIPT")
        lines.append("=" * 70)
        lines.append(summary.get('full_transcript', '[No transcript]'))
        lines.append("")

        # Clip-by-clip ontology
        lines.append("=" * 70)
        lines.append("CLIP-BY-CLIP ONTOLOGY")
        lines.append("=" * 70)

        for clip in annotated_clips:
            lines.append(clip.to_text())

        lines.append("=" * 70)

        # Write text file
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return text_path

    def process_video(self, video_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Full pipeline: analyze video, update ontology, generate outputs."""
        # Analyze
        if self.progress_callback:
            self.progress_callback("Analyzing video with Gemini AI...", 40)
        analysis = self.analyze_video(video_path)

        # Update ontology
        if self.progress_callback:
            self.progress_callback("Updating ontology...", 70)
        annotated_clips = self.update_ontology(analysis)

        # Generate output (text only)
        if self.progress_callback:
            self.progress_callback("Generating output files...", 85)
        text_path = self.generate_output(
            video_path, analysis, annotated_clips, output_dir
        )

        # Save master ontology as text + binary
        if self.progress_callback:
            self.progress_callback("Saving ontology and brain...", 95)
        ontology_text_path = self.ontology_path.replace('.pkl', '.txt')
        self.master_ontology.save(ontology_text_path)
        self.master_ontology.save_binary(self.ontology_path)

        # Save brain as text
        brain_text_path = self.brain_path.replace('.pkl', '.txt')
        with open(brain_text_path, 'w') as f:
            f.write(self.brain.to_text())

        print(f"\n{'='*60}")
        print("COMPLETE")
        print(f"{'='*60}")
        print(f"Clips analyzed: {len(annotated_clips)}")
        print(f"Output: {text_path}")
        print(f"Master ontology: {ontology_text_path}")
        print(f"Brain: {brain_text_path}")

        if self.progress_callback:
            self.progress_callback("Complete!", 100)

        return {
            "video": video_path,
            "clips_count": len(annotated_clips),
            "output": text_path,
            "analysis": analysis
        }
