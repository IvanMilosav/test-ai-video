"""
Clip Ontology Schema
====================
Defines the universal ontology structure for describing video ad clips.
Focus: VISUAL, EMOTIONAL, FUNCTIONAL attributes only.
Pure text output - no JSON.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from datetime import datetime


@dataclass
class OntologyCategory:
    """A category in the ontology that expands with new values."""
    name: str
    values: Set[str] = field(default_factory=set)
    frequency: Dict[str, int] = field(default_factory=dict)

    def add_value(self, value: str):
        if value:
            self.values.add(value)
            self.frequency[value] = self.frequency.get(value, 0) + 1

    def get_top_values(self, n: int = 10) -> List[str]:
        return sorted(self.values, key=lambda v: self.frequency.get(v, 0), reverse=True)[:n]

    def to_text(self) -> str:
        if not self.values:
            return ""
        sorted_vals = self.get_top_values(20)
        lines = []
        for v in sorted_vals:
            lines.append(f"  {v} ({self.frequency.get(v, 0)}x)")
        return "\n".join(lines)


@dataclass
class ClipOntology:
    """
    Ontology for a single clip - VISUAL, EMOTIONAL, FUNCTIONAL only.
    """
    # Temporal
    timestamp_start: str = ""
    timestamp_end: str = ""
    duration_seconds: float = 0.0

    # Script
    script_segment: str = ""  # Verbatim transcript for this clip

    # VISUAL
    shot_type: str = ""
    camera_angle: str = ""
    camera_movement: str = ""
    composition: str = ""
    setting_type: str = ""
    setting_description: str = ""
    lighting_style: str = ""
    color_mood: str = ""
    subject_type: str = ""
    subject_description: str = ""
    subject_action: str = ""
    text_on_screen: List[str] = field(default_factory=list)
    text_purpose: str = ""

    # EMOTIONAL
    primary_emotion: str = ""
    secondary_emotion: str = ""
    emotional_intensity: str = ""
    emotional_direction: str = ""

    # FUNCTIONAL
    clip_function: str = ""
    narrative_role: str = ""
    persuasion_mechanism: str = ""
    persuasion_target: str = ""

    # STRUCTURE
    transition_in: str = ""
    transition_out: str = ""

    # PURPOSE
    purpose_summary: str = ""


@dataclass
class MasterClipOntology:
    """
    Master ontology that evolves across all analyzed videos.
    Tracks all discovered values and their frequencies.
    """
    version: str = "1.0"
    created_at: str = ""
    updated_at: str = ""
    videos_analyzed: int = 0
    total_clips_analyzed: int = 0

    # VISUAL categories
    shot_types: OntologyCategory = field(default_factory=lambda: OntologyCategory("shot_types"))
    camera_angles: OntologyCategory = field(default_factory=lambda: OntologyCategory("camera_angles"))
    camera_movements: OntologyCategory = field(default_factory=lambda: OntologyCategory("camera_movements"))
    compositions: OntologyCategory = field(default_factory=lambda: OntologyCategory("compositions"))
    setting_types: OntologyCategory = field(default_factory=lambda: OntologyCategory("setting_types"))
    lighting_styles: OntologyCategory = field(default_factory=lambda: OntologyCategory("lighting_styles"))
    color_moods: OntologyCategory = field(default_factory=lambda: OntologyCategory("color_moods"))
    subject_types: OntologyCategory = field(default_factory=lambda: OntologyCategory("subject_types"))
    subject_actions: OntologyCategory = field(default_factory=lambda: OntologyCategory("subject_actions"))
    text_purposes: OntologyCategory = field(default_factory=lambda: OntologyCategory("text_purposes"))

    # EMOTIONAL categories
    emotions: OntologyCategory = field(default_factory=lambda: OntologyCategory("emotions"))
    emotional_intensities: OntologyCategory = field(default_factory=lambda: OntologyCategory("emotional_intensities"))

    # FUNCTIONAL categories
    clip_functions: OntologyCategory = field(default_factory=lambda: OntologyCategory("clip_functions"))
    narrative_roles: OntologyCategory = field(default_factory=lambda: OntologyCategory("narrative_roles"))
    persuasion_mechanisms: OntologyCategory = field(default_factory=lambda: OntologyCategory("persuasion_mechanisms"))

    # STRUCTURE
    transition_types: OntologyCategory = field(default_factory=lambda: OntologyCategory("transition_types"))

    # Patterns
    common_sequences: List[List[str]] = field(default_factory=list)
    function_duration_averages: Dict[str, float] = field(default_factory=dict)
    emotion_function_correlations: Dict[str, Dict[str, int]] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def update_from_clip(self, clip: ClipOntology):
        """Update ontology with data from a clip."""
        self.total_clips_analyzed += 1
        self.updated_at = datetime.now().isoformat()

        # Visual
        self.shot_types.add_value(clip.shot_type)
        self.camera_angles.add_value(clip.camera_angle)
        self.camera_movements.add_value(clip.camera_movement)
        self.compositions.add_value(clip.composition)
        self.setting_types.add_value(clip.setting_type)
        self.lighting_styles.add_value(clip.lighting_style)
        self.color_moods.add_value(clip.color_mood)
        self.subject_types.add_value(clip.subject_type)
        self.subject_actions.add_value(clip.subject_action)
        self.text_purposes.add_value(clip.text_purpose)

        # Emotional
        self.emotions.add_value(clip.primary_emotion)
        self.emotions.add_value(clip.secondary_emotion)
        self.emotional_intensities.add_value(clip.emotional_intensity)

        # Functional
        self.clip_functions.add_value(clip.clip_function)
        self.narrative_roles.add_value(clip.narrative_role)
        self.persuasion_mechanisms.add_value(clip.persuasion_mechanism)

        # Structure
        self.transition_types.add_value(clip.transition_in)
        self.transition_types.add_value(clip.transition_out)

        # Track duration by function
        if clip.clip_function and clip.duration_seconds > 0:
            func = clip.clip_function
            if func not in self.function_duration_averages:
                self.function_duration_averages[func] = clip.duration_seconds
            else:
                old_avg = self.function_duration_averages[func]
                count = self.clip_functions.frequency.get(func, 1)
                self.function_duration_averages[func] = (old_avg * (count - 1) + clip.duration_seconds) / count

        # Track emotion-function correlation
        if clip.clip_function and clip.primary_emotion:
            func = clip.clip_function
            emotion = clip.primary_emotion
            if func not in self.emotion_function_correlations:
                self.emotion_function_correlations[func] = {}
            self.emotion_function_correlations[func][emotion] = self.emotion_function_correlations[func].get(emotion, 0) + 1

    def save(self, path: str):
        """Save ontology to text file."""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_text())

    def to_text(self) -> str:
        """Generate full text representation of ontology."""
        lines = []
        lines.append("=" * 70)
        lines.append("MASTER CLIP ONTOLOGY")
        lines.append("=" * 70)
        lines.append(f"Version: {self.version}")
        lines.append(f"Videos Analyzed: {self.videos_analyzed}")
        lines.append(f"Total Clips Analyzed: {self.total_clips_analyzed}")
        lines.append(f"Last Updated: {self.updated_at}")
        lines.append("")

        # Visual
        lines.append("=" * 70)
        lines.append("VISUAL ONTOLOGY")
        lines.append("=" * 70)

        categories = [
            ("Shot Types", self.shot_types),
            ("Camera Angles", self.camera_angles),
            ("Camera Movements", self.camera_movements),
            ("Compositions", self.compositions),
            ("Setting Types", self.setting_types),
            ("Lighting Styles", self.lighting_styles),
            ("Color Moods", self.color_moods),
            ("Subject Types", self.subject_types),
            ("Subject Actions", self.subject_actions),
            ("Text Purposes", self.text_purposes),
        ]

        for name, cat in categories:
            if cat.values:
                lines.append(f"\n{name}:")
                lines.append(cat.to_text())

        # Emotional
        lines.append("")
        lines.append("=" * 70)
        lines.append("EMOTIONAL ONTOLOGY")
        lines.append("=" * 70)

        if self.emotions.values:
            lines.append("\nEmotions:")
            lines.append(self.emotions.to_text())
        if self.emotional_intensities.values:
            lines.append("\nIntensities:")
            lines.append(self.emotional_intensities.to_text())

        # Functional
        lines.append("")
        lines.append("=" * 70)
        lines.append("FUNCTIONAL ONTOLOGY")
        lines.append("=" * 70)

        if self.clip_functions.values:
            lines.append("\nClip Functions:")
            lines.append(self.clip_functions.to_text())
        if self.narrative_roles.values:
            lines.append("\nNarrative Roles:")
            lines.append(self.narrative_roles.to_text())
        if self.persuasion_mechanisms.values:
            lines.append("\nPersuasion Mechanisms:")
            lines.append(self.persuasion_mechanisms.to_text())

        # Transitions
        if self.transition_types.values:
            lines.append("")
            lines.append("=" * 70)
            lines.append("TRANSITIONS")
            lines.append("=" * 70)
            lines.append(self.transition_types.to_text())

        # Patterns
        if self.function_duration_averages:
            lines.append("")
            lines.append("=" * 70)
            lines.append("FUNCTION DURATION AVERAGES")
            lines.append("=" * 70)
            for func, avg in sorted(self.function_duration_averages.items(), key=lambda x: x[1]):
                lines.append(f"  {func}: {avg:.2f}s")

        if self.emotion_function_correlations:
            lines.append("")
            lines.append("=" * 70)
            lines.append("EMOTION-FUNCTION CORRELATIONS")
            lines.append("=" * 70)
            for func, emotions in sorted(self.emotion_function_correlations.items()):
                top = sorted(emotions.items(), key=lambda x: -x[1])[:3]
                emotion_str = ", ".join([f"{e}({c})" for e, c in top])
                lines.append(f"  {func}: {emotion_str}")

        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    @classmethod
    def load(cls, path: str) -> 'MasterClipOntology':
        """Load ontology from text file (parses the text format)."""
        # For simplicity, we'll use a simple serialization
        # In practice, you might want pickle or a custom format
        import pickle
        pickle_path = path.replace('.txt', '.pkl')
        if os.path.exists(pickle_path):
            with open(pickle_path, 'rb') as f:
                return pickle.load(f)
        return cls()

    def save_binary(self, path: str):
        """Save to pickle for easy reload."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump(self, f)

    @classmethod
    def load_binary(cls, path: str) -> 'MasterClipOntology':
        """Load from pickle."""
        import pickle
        if os.path.exists(path):
            with open(path, 'rb') as f:
                return pickle.load(f)
        return cls()


@dataclass
class AnnotatedClip:
    """A clip with its ontology annotation for text output."""
    clip_number: int
    ontology: ClipOntology

    def to_text(self) -> str:
        """Generate text block for this clip."""
        o = self.ontology
        lines = []

        lines.append("─" * 70)
        lines.append(f"CLIP {self.clip_number}")
        lines.append(f"Timestamp: {o.timestamp_start} → {o.timestamp_end} ({o.duration_seconds:.2f}s)")
        lines.append("─" * 70)

        # Script
        lines.append("")
        lines.append("SCRIPT SEGMENT:")
        if o.script_segment:
            lines.append(f'  "{o.script_segment}"')
        else:
            lines.append("  [No speech]")

        # Visual
        lines.append("")
        lines.append("VISUAL:")
        lines.append(f"  Shot: {o.shot_type}")
        lines.append(f"  Camera: {o.camera_angle} / {o.camera_movement}")
        lines.append(f"  Composition: {o.composition}")
        lines.append(f"  Setting: {o.setting_type} - {o.setting_description}")
        lines.append(f"  Lighting: {o.lighting_style}")
        lines.append(f"  Color: {o.color_mood}")
        lines.append(f"  Subject: {o.subject_type} - {o.subject_action}")
        lines.append(f"  Subject Detail: {o.subject_description}")
        if o.text_on_screen:
            lines.append(f"  Text On Screen: {' | '.join(o.text_on_screen)}")
            lines.append(f"  Text Purpose: {o.text_purpose}")

        # Emotional
        lines.append("")
        lines.append("EMOTIONAL:")
        lines.append(f"  Primary: {o.primary_emotion}")
        if o.secondary_emotion:
            lines.append(f"  Secondary: {o.secondary_emotion}")
        lines.append(f"  Intensity: {o.emotional_intensity}")
        lines.append(f"  Direction: {o.emotional_direction}")

        # Functional
        lines.append("")
        lines.append("FUNCTIONAL:")
        lines.append(f"  Function: {o.clip_function}")
        lines.append(f"  Narrative Role: {o.narrative_role}")
        lines.append(f"  Persuasion: {o.persuasion_mechanism} → {o.persuasion_target}")

        # Transitions
        lines.append("")
        lines.append(f"TRANSITIONS: {o.transition_in} → {o.transition_out}")

        # Purpose
        lines.append("")
        lines.append("PURPOSE:")
        lines.append(f"  {o.purpose_summary}")

        lines.append("")
        return "\n".join(lines)


# Import os for file operations
import os
