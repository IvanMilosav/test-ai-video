#!/usr/bin/env python3
"""
Batch Processor for Iterative Clip Ontology Building
=====================================================
Processes a directory of videos one at a time, building the ontology iteratively.
Each video refines and expands the universal clip ontology.

Usage:
    python batch_processor.py /path/to/videos
    python batch_processor.py /path/to/videos --output ./results
    python batch_processor.py /path/to/videos --model flash
    python batch_processor.py --status  # Show current ontology status
"""

import argparse
import os
import sys
import glob
import json
from datetime import datetime
from typing import List, Optional

from config import Config
from iterative_analyzer import IterativeClipAnalyzer
from clip_ontology_schema import MasterClipOntology


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║               ITERATIVE CLIP ONTOLOGY BUILDER                                ║
║                                                                              ║
║  Processes videos sequentially to build a universal clip ontology.          ║
║  Each video analyzed expands and refines the ontology.                       ║
║                                                                              ║
║  The ontology becomes more comprehensive and vertical-agnostic over time.   ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)


def find_videos(directory: str, extensions: List[str] = None) -> List[str]:
    """Find all video files in directory."""
    if extensions is None:
        extensions = ['.mp4', '.mov', '.webm', '.avi', '.mkv']

    videos = []
    for ext in extensions:
        pattern = os.path.join(directory, f'*{ext}')
        videos.extend(glob.glob(pattern))
        # Also check lowercase
        pattern = os.path.join(directory, f'*{ext.upper()}')
        videos.extend(glob.glob(pattern))

    # Remove duplicates and sort
    videos = sorted(list(set(videos)))
    return videos


def get_processing_log_path(output_dir: str) -> str:
    """Get path to processing log file."""
    return os.path.join(output_dir, 'processing_log.json')


def load_processing_log(output_dir: str) -> dict:
    """Load or create processing log."""
    log_path = get_processing_log_path(output_dir)
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            return json.load(f)
    return {
        "started": datetime.now().isoformat(),
        "processed": [],
        "failed": [],
        "skipped": []
    }


def save_processing_log(output_dir: str, log: dict):
    """Save processing log."""
    log_path = get_processing_log_path(output_dir)
    log["last_updated"] = datetime.now().isoformat()
    with open(log_path, 'w') as f:
        json.dump(log, f, indent=2)


def show_ontology_status(ontology_path: str):
    """Display current ontology status."""
    if not os.path.exists(ontology_path):
        print(f"No ontology found at: {ontology_path}")
        print("Process some videos first to build the ontology.")
        return

    ontology = MasterClipOntology.load_binary(ontology_path)
    print(ontology.to_text())


def process_directory(
    video_dir: str,
    output_dir: str = None,
    model: str = "pro",
    ontology_path: str = None,
    resume: bool = True,
    limit: Optional[int] = None
):
    """
    Process all videos in a directory iteratively.

    Args:
        video_dir: Directory containing videos
        output_dir: Output directory (default: video_dir/ontology_output)
        model: Model to use (pro, flash)
        ontology_path: Path to ontology file
        resume: Skip already processed videos
        limit: Maximum number of videos to process
    """
    # Setup directories
    if output_dir is None:
        output_dir = os.path.join(video_dir, 'ontology_output')
    os.makedirs(output_dir, exist_ok=True)

    if ontology_path is None:
        ontology_path = os.path.join(output_dir, 'master_clip_ontology.pkl')

    # Find videos
    videos = find_videos(video_dir)

    if not videos:
        print(f"No video files found in: {video_dir}")
        return

    print(f"Found {len(videos)} videos in: {video_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Ontology path: {ontology_path}")
    print(f"Model: {model}")
    print()

    # Load processing log
    log = load_processing_log(output_dir)

    # Filter already processed if resuming
    if resume:
        processed_files = set(log.get('processed', []))
        videos = [v for v in videos if os.path.basename(v) not in processed_files]
        if not videos:
            print("All videos already processed. Use --no-resume to reprocess.")
            return
        print(f"Resuming: {len(videos)} videos remaining")

    # Apply limit
    if limit:
        videos = videos[:limit]
        print(f"Processing first {limit} videos")

    print()
    print("=" * 70)

    # Initialize analyzer
    analyzer = IterativeClipAnalyzer(
        model=model,
        ontology_path=ontology_path
    )

    # Process each video
    total = len(videos)
    for i, video_path in enumerate(videos, 1):
        video_name = os.path.basename(video_path)

        print()
        print(f"[{i}/{total}] Processing: {video_name}")
        print("-" * 70)

        try:
            # Process video
            result = analyzer.process_video(video_path, output_dir)

            # Log success
            log['processed'].append(video_name)
            save_processing_log(output_dir, log)

            print(f"[{i}/{total}] Complete: {result['clips_count']} clips analyzed")

        except Exception as e:
            print(f"[{i}/{total}] ERROR: {str(e)}")

            # Log failure
            log['failed'].append({
                "video": video_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
            save_processing_log(output_dir, log)

            # Continue with next video
            continue

    # Final summary
    print()
    print("=" * 70)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 70)
    print(f"Processed: {len(log['processed'])} videos")
    print(f"Failed: {len(log['failed'])} videos")

    # Show ontology summary
    print()
    show_ontology_status(ontology_path)


def main():
    parser = argparse.ArgumentParser(
        description="Process videos iteratively to build clip ontology",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/videos
      Process all videos in directory

  %(prog)s /path/to/videos --output ./results
      Save outputs to specific directory

  %(prog)s /path/to/videos --model flash
      Use faster model

  %(prog)s /path/to/videos --limit 5
      Process only first 5 videos

  %(prog)s --status
      Show current ontology status

  %(prog)s /path/to/videos --no-resume
      Reprocess all videos (ignore previous progress)
        """
    )

    parser.add_argument(
        'video_dir',
        nargs='?',
        help='Directory containing video files'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output directory for results'
    )
    parser.add_argument(
        '--model', '-m',
        choices=['pro', 'flash'],
        default='pro',
        help='Model to use: pro (best accuracy) or flash (faster)'
    )
    parser.add_argument(
        '--ontology',
        help='Path to ontology file'
    )
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Reprocess all videos, ignoring previous progress'
    )
    parser.add_argument(
        '--limit', '-n',
        type=int,
        help='Maximum number of videos to process'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show current ontology status'
    )

    args = parser.parse_args()

    print_banner()

    # Check API key via Config
    if not Config.GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not configured")
        print("\nSet it in config.py or .env file")
        sys.exit(1)

    # Handle status request
    if args.status:
        ontology_path = args.ontology or 'master_clip_ontology.pkl'
        show_ontology_status(ontology_path)
        return

    # Require video directory for processing
    if not args.video_dir:
        parser.print_help()
        print("\nERROR: video_dir is required")
        sys.exit(1)

    if not os.path.isdir(args.video_dir):
        print(f"ERROR: Not a directory: {args.video_dir}")
        sys.exit(1)

    # Process
    try:
        process_directory(
            video_dir=args.video_dir,
            output_dir=args.output,
            model=args.model,
            ontology_path=args.ontology,
            resume=not args.no_resume,
            limit=args.limit
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved.")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
