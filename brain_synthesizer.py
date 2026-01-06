#!/usr/bin/env python3
"""
Brain Synthesizer
=================
Takes all analyzed video ontologies and synthesizes them into a master
cinematographic playbook using Gemini.

This is NOT statistics collection. This is SYNTHESIS - using AI to identify
patterns, categorize shot types, define conceptual boundaries, and create
a vertical-agnostic guide for clip selection.

Run this AFTER processing videos to generate the brain.
"""

import os
import sys
import glob
import json
from datetime import datetime
from google import genai

from config import Config


def find_ontology_files(directory: str) -> list:
    """Find all ontology text files in directory."""
    patterns = [
        os.path.join(directory, '*_ontology_*.txt'),
        os.path.join(directory, '**/*_ontology_*.txt'),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    return sorted(set(files))


def read_ontology_files(files: list) -> str:
    """Read and combine all ontology files into one document."""
    combined = []
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            combined.append(f"=== FILE: {os.path.basename(f)} ===\n{content}\n")
    return "\n".join(combined)


def synthesize_brain(ontologies_text: str, output_path: str):
    """
    Use Gemini to synthesize all ontologies into a master cinematographic playbook.
    """
    if not Config.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured")

    client = genai.Client(api_key=Config.GOOGLE_API_KEY)
    model = "gemini-3-pro-preview"  # Use pro for this important synthesis

    prompt = f'''You are an expert cinematographer and video editor analyzing a collection of video ad breakdowns.

Below are detailed clip-by-clip ontologies from multiple video advertisements. Your task is to synthesize these into a MASTER CINEMATOGRAPHIC PLAYBOOK that can guide clip selection for ANY video ad, regardless of vertical/industry.

ANALYZED VIDEOS:
"""
{ontologies_text}
"""

Create a comprehensive SCRIPT-TO-CLIP PLAYBOOK with these sections:

================================================================================
SECTION 1: SHOT TYPE TAXONOMY
================================================================================
Categorize ALL the shot types you observe into a clear taxonomy:

A) PROTAGONIST/HERO SHOTS
   - Define what makes a protagonist shot
   - Variations observed (talking head, action, reaction, etc.)
   - When to use each variation
   - Examples from the data with script context

B) PRODUCT/SUBJECT SHOTS
   - Hero product shots
   - Detail/insert shots
   - Product-in-use shots
   - Product-with-person shots
   - Examples from the data

C) B-ROLL CATEGORIES
   - Contextual b-roll (establishes setting/mood)
   - Illustrative b-roll (visualizes a concept)
   - Transitional b-roll (covers edits, pacing)
   - Atmospheric b-roll (emotion/tone)
   - Examples from the data

D) TEXT/GRAPHIC SHOTS
   - Title cards
   - Statistic callouts
   - Quote overlays
   - CTA screens
   - Lower thirds
   - Examples from the data

E) SCREEN RECORDINGS/DEMOS
   - Full screen capture
   - Partial/window capture
   - Animated demos
   - Examples from the data

================================================================================
SECTION 2: CONCEPTUAL BOUNDARIES
================================================================================
Define what creates a "conceptual boundary" - the point where a new clip is needed.

CRITICAL RULE: If a script line takes longer than ~3 seconds to speak, it almost
certainly needs to be broken into multiple clips. Analyze the data to understand
HOW these longer lines are broken up visually.

A) THE 3-SECOND RULE
   - Find examples where a single spoken thought spans multiple clips
   - Identify WHERE in the sentence the visual cut happens
   - Document the patterns:
     * Cut on conjunctions ("and", "but", "so")
     * Cut on commas/natural pauses
     * Cut when a new concept/noun is introduced
     * Cut to illustrate what's being described
   - Provide specific examples from the data showing:
     SCRIPT: "[full sentence]"
     CLIP 1: "[first part]" → [visual]
     CLIP 2: "[second part]" → [visual]

B) SCRIPT-DRIVEN BOUNDARIES
   - When script content requires a visual change
   - Examples: "When the script mentions [X], cut to [Y]"
   - Identify trigger words that demand a visual change

C) EMOTIONAL BOUNDARIES
   - When tone/emotion shifts require visual change
   - Examples from the data

D) STRUCTURAL BOUNDARIES
   - Hook -> Problem -> Solution -> Proof -> CTA transitions
   - What clips typically mark each transition
   - Examples from the data

E) PACING BOUNDARIES
   - When to cut for energy/rhythm even without content change
   - Visual variety rules
   - How often to cut away from talking head to maintain engagement

================================================================================
SECTION 3: PROTAGONIST/HERO USAGE PATTERNS
================================================================================
How the main speaker/presenter is used:

A) WHEN TO SHOW THE PROTAGONIST
   - Script content that calls for protagonist
   - Functions (hook, credibility, connection, CTA)

B) WHEN TO CUT AWAY FROM PROTAGONIST
   - What triggers a cutaway
   - What to cut away TO
   - How long before returning

C) PROTAGONIST SHOT VARIATIONS
   - Close-up vs medium vs wide - when to use each
   - Direct address vs candid
   - Solo vs with product vs with others

================================================================================
SECTION 4: SCRIPT-TO-CLIP MATCHING RULES
================================================================================
Specific rules for what clip type to use based on script content.

Format each rule as:
WHEN script contains/mentions [X] → USE [clip type]
Example from data: "[actual script]" → [what was shown]

Categories:
- Product mentions
- Problem/pain statements
- Solution statements
- Benefit claims
- Social proof/testimonials
- Statistics/numbers
- Calls to action
- Emotional appeals
- Questions (rhetorical or direct)
- Demonstrations/how-to

================================================================================
SECTION 5: TRANSITION PATTERNS
================================================================================
What clip types naturally flow into what:

A) COMMON SEQUENCES
   - List observed clip type sequences
   - Why they work

B) AWKWARD TRANSITIONS TO AVOID
   - What doesn't flow well

================================================================================
SECTION 6: VERTICAL-AGNOSTIC PRINCIPLES
================================================================================
Universal rules that apply regardless of industry:

- Core cinematographic principles observed
- Pacing principles
- Visual hierarchy principles
- Attention management principles

================================================================================

OUTPUT FORMAT:
- Write in clear, actionable language
- Include specific examples from the analyzed videos
- Make it a REFERENCE GUIDE someone can use while editing
- No statistics or percentages - just rules and examples
- Be thorough but organized

Generate the complete playbook now.'''

    print("Synthesizing brain from all ontologies...")
    print("This may take a minute...")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            'temperature': 0.7,
            'max_output_tokens': 8192,
        }
    )

    brain_text = response.text

    # Add header
    final_output = f"""{'=' * 80}
MASTER SCRIPT-TO-CLIP PLAYBOOK
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: Synthesized from {len(find_ontology_files(os.path.dirname(output_path) or '.'))} video analyses

This playbook provides cinematographic guidance for matching clips to script
content. It is vertical-agnostic and based on patterns observed across
multiple video advertisements.

{'=' * 80}

{brain_text}
"""

    # Save
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_output)

    print(f"\nBrain synthesized and saved to: {output_path}")
    return final_output


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Synthesize all video ontologies into a master playbook"
    )
    parser.add_argument(
        'input_dir',
        help='Directory containing ontology files (or path to search recursively)'
    )
    parser.add_argument(
        '--output', '-o',
        default='script_clip_brain.txt',
        help='Output path for the brain/playbook (default: script_clip_brain.txt)'
    )

    args = parser.parse_args()

    # Find ontology files
    if os.path.isdir(args.input_dir):
        files = find_ontology_files(args.input_dir)
    else:
        print(f"ERROR: {args.input_dir} is not a directory")
        sys.exit(1)

    if not files:
        print(f"No ontology files found in: {args.input_dir}")
        print("Run parallel_processor.py on your videos first.")
        sys.exit(1)

    print(f"Found {len(files)} ontology files:")
    for f in files[:10]:
        print(f"  - {os.path.basename(f)}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more")
    print()

    # Read all ontologies
    print("Reading ontology files...")
    ontologies_text = read_ontology_files(files)
    print(f"Total content: {len(ontologies_text):,} characters")
    print()

    # Check size - if too large, we may need to summarize first
    if len(ontologies_text) > 500000:  # ~500KB
        print("WARNING: Large amount of data. May need to process in batches.")
        print("Truncating to most recent files...")
        # Take most recent files (they're sorted by name which includes timestamp)
        files = files[-20:]
        ontologies_text = read_ontology_files(files)
        print(f"Using {len(files)} most recent files")

    # Synthesize
    synthesize_brain(ontologies_text, args.output)


if __name__ == "__main__":
    main()
