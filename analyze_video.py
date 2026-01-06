#!/usr/bin/env python3
"""
Single Video Analyzer
=====================
Convenience script to analyze a single video and update the ontology.

Usage:
    python analyze_video.py video.mp4
    python analyze_video.py video.mp4 --model flash
    python analyze_video.py video.mp4 --output ./results
"""

import argparse
import os
import sys

from config import Config
from iterative_analyzer import IterativeClipAnalyzer


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a single video and update the clip ontology"
    )

    parser.add_argument(
        'video_path',
        help='Path to video file'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory'
    )
    parser.add_argument(
        '--model', '-m',
        choices=['pro', 'flash'],
        default='pro',
        help='Model: pro (best) or flash (faster)'
    )
    parser.add_argument(
        '--ontology',
        default='master_clip_ontology.pkl',
        help='Path to ontology file'
    )

    args = parser.parse_args()

    # Check API key via Config
    if not Config.GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not configured")
        print("Set it in config.py or .env file")
        sys.exit(1)

    # Check video exists
    if not os.path.exists(args.video_path):
        print(f"ERROR: Video not found: {args.video_path}")
        sys.exit(1)

    print("╔" + "═" * 58 + "╗")
    print("║" + " CLIP ONTOLOGY ANALYZER ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    try:
        analyzer = IterativeClipAnalyzer(
            model=args.model,
            ontology_path=args.ontology
        )

        result = analyzer.process_video(args.video_path, args.output)

        print()
        print(f"Output: {result['output']}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
