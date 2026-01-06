#!/usr/bin/env python3
"""
Ontology Reporter
=================
Generates reports showing the current state of the clip ontology
and how it has evolved across analyzed videos.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

from clip_ontology_schema import MasterClipOntology


class OntologyReporter:
    """Generates various reports from the master ontology."""

    def __init__(self, ontology_path: str = "master_clip_ontology.json"):
        self.ontology_path = ontology_path

        if not os.path.exists(ontology_path):
            raise FileNotFoundError(f"Ontology not found: {ontology_path}")

        self.ontology = MasterClipOntology.load(ontology_path)

    def generate_full_report(self) -> str:
        """Generate comprehensive text report of the ontology."""
        lines = []
        o = self.ontology

        lines.append("╔" + "═" * 68 + "╗")
        lines.append("║" + " MASTER CLIP ONTOLOGY REPORT ".center(68) + "║")
        lines.append("╚" + "═" * 68 + "╝")
        lines.append("")

        # Metadata
        lines.append("METADATA")
        lines.append("-" * 40)
        lines.append(f"Version: {o.version}")
        lines.append(f"Created: {o.created_at}")
        lines.append(f"Last Updated: {o.updated_at}")
        lines.append(f"Videos Analyzed: {o.videos_analyzed}")
        lines.append(f"Total Clips Analyzed: {o.total_clips_analyzed}")
        if o.videos_analyzed > 0:
            avg_clips = o.total_clips_analyzed / o.videos_analyzed
            lines.append(f"Average Clips per Video: {avg_clips:.1f}")
        lines.append("")

        # Category summaries
        categories = [
            ("SHOT TYPES", o.shot_types, "How the camera frames the subject"),
            ("CAMERA ANGLES", o.camera_angles, "Camera height/position relative to subject"),
            ("CAMERA MOVEMENTS", o.camera_movements, "How the camera moves during the clip"),
            ("COMPOSITIONS", o.compositions, "How elements are arranged in frame"),
            ("SETTING TYPES", o.setting_types, "Types of environments/locations"),
            ("LIGHTING STYLES", o.lighting_styles, "Lighting approaches"),
            ("COLOR MOODS", o.color_moods, "Overall color/mood palettes"),
            ("SUBJECT TYPES", o.subject_types, "What the clip focuses on"),
            ("SUBJECT ACTIONS", o.subject_actions, "What subjects do in clips"),
            ("TEXT PURPOSES", o.text_purposes, "Why text appears on screen"),
            ("SPEAKER TYPES", o.speaker_types, "Who is speaking"),
            ("VOCAL TONES", o.vocal_tones, "Tone of voice delivery"),
            ("VOCAL PACINGS", o.vocal_pacings, "Speed of speech"),
            ("MUSIC STYLES", o.music_styles, "Types of background music"),
            ("EMOTIONS", o.emotions, "Emotions evoked by clips"),
            ("EMOTIONAL INTENSITIES", o.emotional_intensities, "How strong the emotion"),
            ("CLIP FUNCTIONS", o.clip_functions, "Role of clip in ad structure"),
            ("NARRATIVE ROLES", o.narrative_roles, "Role in story arc"),
            ("PERSUASION MECHANISMS", o.persuasion_mechanisms, "Psychological techniques"),
            ("TRANSITION TYPES", o.transition_types, "How clips connect"),
        ]

        for title, category, description in categories:
            if category.values:
                lines.append("=" * 70)
                lines.append(title)
                lines.append(f"({description})")
                lines.append("-" * 70)

                # Sort by frequency
                sorted_vals = sorted(
                    category.values,
                    key=lambda v: category.frequency.get(v, 0),
                    reverse=True
                )

                total_occurrences = sum(category.frequency.values())

                for value in sorted_vals:
                    freq = category.frequency.get(value, 0)
                    pct = (freq / total_occurrences * 100) if total_occurrences > 0 else 0
                    bar_len = int(pct / 2)  # 50 char max bar
                    bar = "█" * bar_len

                    # Description if available
                    desc = category.value_descriptions.get(value, "")
                    desc_str = f" - {desc}" if desc else ""

                    lines.append(f"  {value}")
                    lines.append(f"    {bar} {freq}x ({pct:.1f}%){desc_str}")

                lines.append("")

        # Function duration averages
        if o.function_duration_averages:
            lines.append("=" * 70)
            lines.append("CLIP FUNCTION DURATION AVERAGES")
            lines.append("-" * 70)

            sorted_funcs = sorted(
                o.function_duration_averages.items(),
                key=lambda x: x[1]
            )

            for func, avg_dur in sorted_funcs:
                bar_len = int(avg_dur * 5)  # 5 chars per second
                bar = "▓" * min(bar_len, 50)
                lines.append(f"  {func}: {bar} {avg_dur:.2f}s")

            lines.append("")

        # Emotion-function correlations
        if o.emotion_function_correlations:
            lines.append("=" * 70)
            lines.append("EMOTION-FUNCTION CORRELATIONS")
            lines.append("(Which emotions are triggered by which clip functions)")
            lines.append("-" * 70)

            for func, emotions in sorted(o.emotion_function_correlations.items()):
                top_emotions = sorted(emotions.items(), key=lambda x: -x[1])[:3]
                emotion_str = ", ".join([f"{e}({c})" for e, c in top_emotions])
                lines.append(f"  {func}: {emotion_str}")

            lines.append("")

        # Common sequences
        if o.common_sequences:
            lines.append("=" * 70)
            lines.append("COMMON CLIP FUNCTION SEQUENCES")
            lines.append("(How clips are typically ordered)")
            lines.append("-" * 70)

            # Find most common starting sequences (first 5 functions)
            seq_counts: Dict[str, int] = {}
            for seq in o.common_sequences[-100:]:  # Last 100 sequences
                key = " → ".join(seq[:5])
                seq_counts[key] = seq_counts.get(key, 0) + 1

            sorted_seqs = sorted(seq_counts.items(), key=lambda x: -x[1])[:10]

            for seq, count in sorted_seqs:
                lines.append(f"  ({count}x) {seq}")

            lines.append("")

        lines.append("=" * 70)
        lines.append(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_category_values(self) -> str:
        """Generate a simple list of all known values per category."""
        lines = []
        o = self.ontology

        lines.append("CLIP ONTOLOGY - KNOWN VALUES")
        lines.append("=" * 50)
        lines.append("")

        categories = [
            ("shot_types", o.shot_types),
            ("camera_angles", o.camera_angles),
            ("camera_movements", o.camera_movements),
            ("compositions", o.compositions),
            ("setting_types", o.setting_types),
            ("lighting_styles", o.lighting_styles),
            ("color_moods", o.color_moods),
            ("subject_types", o.subject_types),
            ("subject_actions", o.subject_actions),
            ("text_purposes", o.text_purposes),
            ("speaker_types", o.speaker_types),
            ("vocal_tones", o.vocal_tones),
            ("vocal_pacings", o.vocal_pacings),
            ("music_styles", o.music_styles),
            ("emotions", o.emotions),
            ("emotional_intensities", o.emotional_intensities),
            ("clip_functions", o.clip_functions),
            ("narrative_roles", o.narrative_roles),
            ("persuasion_mechanisms", o.persuasion_mechanisms),
            ("transition_types", o.transition_types),
        ]

        for name, category in categories:
            if category.values:
                sorted_vals = sorted(
                    category.values,
                    key=lambda v: category.frequency.get(v, 0),
                    reverse=True
                )
                lines.append(f"{name}:")
                lines.append(f"  {', '.join(sorted_vals)}")
                lines.append("")

        return "\n".join(lines)

    def generate_json_export(self) -> dict:
        """Export ontology as JSON for external use."""
        return self.ontology.to_dict()

    def get_stats(self) -> dict:
        """Get quick statistics about the ontology."""
        o = self.ontology

        total_categories = 0
        total_values = 0

        categories = [
            o.shot_types, o.camera_angles, o.camera_movements, o.compositions,
            o.setting_types, o.lighting_styles, o.color_moods, o.subject_types,
            o.subject_actions, o.text_purposes, o.speaker_types, o.vocal_tones,
            o.vocal_pacings, o.music_styles, o.emotions, o.emotional_intensities,
            o.clip_functions, o.narrative_roles, o.persuasion_mechanisms,
            o.transition_types
        ]

        for cat in categories:
            if cat.values:
                total_categories += 1
                total_values += len(cat.values)

        return {
            "videos_analyzed": o.videos_analyzed,
            "total_clips_analyzed": o.total_clips_analyzed,
            "categories_populated": total_categories,
            "total_unique_values": total_values,
            "avg_clips_per_video": (
                o.total_clips_analyzed / o.videos_analyzed
                if o.videos_analyzed > 0 else 0
            ),
            "clip_functions_discovered": len(o.clip_functions.values),
            "emotions_discovered": len(o.emotions.values),
            "created": o.created_at,
            "updated": o.updated_at
        }


def main():
    """CLI for ontology reporting."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate reports from the master clip ontology"
    )

    parser.add_argument(
        'ontology_path',
        nargs='?',
        default='master_clip_ontology.json',
        help='Path to ontology file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Save report to file'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['full', 'values', 'stats', 'json'],
        default='full',
        help='Report format'
    )

    args = parser.parse_args()

    try:
        reporter = OntologyReporter(args.ontology_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Generate report
    if args.format == 'full':
        output = reporter.generate_full_report()
    elif args.format == 'values':
        output = reporter.generate_category_values()
    elif args.format == 'stats':
        stats = reporter.get_stats()
        output = json.dumps(stats, indent=2)
    elif args.format == 'json':
        output = json.dumps(reporter.generate_json_export(), indent=2)

    # Output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Report saved to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
