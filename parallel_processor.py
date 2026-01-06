#!/usr/bin/env python3
"""
Parallel Video Processor
========================
Splits videos into 40-second chunks, processes each in parallel threads,
then assembles results with proper timestamp offsets.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import threading

from config import Config
from clip_ontology_schema import ClipOntology, MasterClipOntology, AnnotatedClip
from iterative_analyzer import IterativeClipAnalyzer


CHUNK_DURATION = 40  # seconds


@dataclass
class VideoChunk:
    """Represents a chunk of video to process."""
    chunk_index: int
    chunk_path: str
    start_offset: float  # seconds from start of original video
    duration: float


@dataclass
class ChunkResult:
    """Result from processing a single chunk."""
    chunk_index: int
    start_offset: float
    clips: List[AnnotatedClip]
    transcript: str
    success: bool
    error: Optional[str] = None


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        raise RuntimeError(f"Could not get video duration: {e}")


def split_video_into_chunks(
    video_path: str,
    chunk_duration: int = CHUNK_DURATION,
    output_dir: str = None
) -> List[VideoChunk]:
    """
    Split video into chunks of specified duration.
    Returns list of VideoChunk objects.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="video_chunks_")

    total_duration = get_video_duration(video_path)
    chunks = []

    chunk_index = 0
    current_time = 0.0

    print(f"Splitting {total_duration:.1f}s video into {chunk_duration}s chunks...")

    while current_time < total_duration:
        # Calculate this chunk's duration
        remaining = total_duration - current_time
        this_chunk_duration = min(chunk_duration, remaining)

        # Output path for this chunk
        chunk_filename = f"chunk_{chunk_index:03d}.mp4"
        chunk_path = os.path.join(output_dir, chunk_filename)

        # Use ffmpeg to extract chunk
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(current_time),
            '-i', video_path,
            '-t', str(this_chunk_duration),
            '-c', 'copy',  # Fast copy without re-encoding
            '-avoid_negative_ts', 'make_zero',
            chunk_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            # If copy fails, try with re-encoding
            cmd = [
                'ffmpeg', '-y',
                '-ss', str(current_time),
                '-i', video_path,
                '-t', str(this_chunk_duration),
                '-c:v', 'libx264', '-preset', 'ultrafast',
                '-c:a', 'aac',
                chunk_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)

        chunks.append(VideoChunk(
            chunk_index=chunk_index,
            chunk_path=chunk_path,
            start_offset=current_time,
            duration=this_chunk_duration
        ))

        current_time += chunk_duration
        chunk_index += 1

    print(f"Created {len(chunks)} chunks")
    return chunks


def add_time_offset(timestamp: str, offset_seconds: float) -> str:
    """Add offset to MM:SS.mmm timestamp and return new timestamp."""
    if not timestamp:
        return timestamp

    try:
        # Parse MM:SS.mmm or MM:SS
        parts = timestamp.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])

        total_seconds = minutes * 60 + seconds + offset_seconds

        new_minutes = int(total_seconds // 60)
        new_seconds = total_seconds % 60

        return f"{new_minutes:02d}:{new_seconds:06.3f}"
    except:
        return timestamp


def process_single_chunk(
    chunk: VideoChunk,
    model: str = "pro",
    thread_id: int = 0
) -> ChunkResult:
    """Process a single video chunk. Runs in a thread."""
    print(f"  [Thread {thread_id}] Processing chunk {chunk.chunk_index} "
          f"({chunk.start_offset:.1f}s - {chunk.start_offset + chunk.duration:.1f}s)")

    try:
        # Create analyzer for this thread (each thread needs its own client)
        analyzer = IterativeClipAnalyzer(model=model)

        # Analyze the chunk
        analysis = analyzer.analyze_video(chunk.chunk_path)

        # Convert to annotated clips
        clips = []
        raw_clips = analysis.get('clips', [])

        for clip_data in raw_clips:
            clip_ontology = analyzer._convert_to_clip_ontology(clip_data)

            # Add time offset to timestamps
            clip_ontology.timestamp_start = add_time_offset(
                clip_ontology.timestamp_start, chunk.start_offset
            )
            clip_ontology.timestamp_end = add_time_offset(
                clip_ontology.timestamp_end, chunk.start_offset
            )

            clips.append(AnnotatedClip(
                clip_number=0,  # Will be renumbered later
                ontology=clip_ontology
            ))

        transcript = analysis.get('video_summary', {}).get('full_transcript', '')

        print(f"  [Thread {thread_id}] Chunk {chunk.chunk_index} complete: {len(clips)} clips")

        return ChunkResult(
            chunk_index=chunk.chunk_index,
            start_offset=chunk.start_offset,
            clips=clips,
            transcript=transcript,
            success=True
        )

    except Exception as e:
        print(f"  [Thread {thread_id}] Chunk {chunk.chunk_index} FAILED: {e}")
        return ChunkResult(
            chunk_index=chunk.chunk_index,
            start_offset=chunk.start_offset,
            clips=[],
            transcript='',
            success=False,
            error=str(e)
        )


def assemble_results(
    chunk_results: List[ChunkResult],
    master_ontology: MasterClipOntology
) -> tuple:
    """
    Assemble chunk results into final ordered list.
    Returns (annotated_clips, full_transcript).
    """
    # Sort by chunk index
    sorted_results = sorted(chunk_results, key=lambda r: r.chunk_index)

    all_clips = []
    transcript_parts = []

    for result in sorted_results:
        if result.success:
            all_clips.extend(result.clips)
            if result.transcript:
                transcript_parts.append(result.transcript)
        else:
            # Add placeholder for failed chunk
            transcript_parts.append(f"[Chunk {result.chunk_index} failed: {result.error}]")

    # Renumber clips sequentially
    for i, clip in enumerate(all_clips, 1):
        clip.clip_number = i
        # Update master ontology
        master_ontology.update_from_clip(clip.ontology)

    full_transcript = ' '.join(transcript_parts)

    return all_clips, full_transcript


class ParallelVideoProcessor:
    """
    Processes videos by splitting into chunks and analyzing in parallel.
    """

    def __init__(
        self,
        model: str = "pro",
        ontology_path: str = "master_clip_ontology.pkl",
        max_workers: int = 4,
        chunk_duration: int = CHUNK_DURATION
    ):
        self.model = model
        self.ontology_path = ontology_path
        self.max_workers = max_workers
        self.chunk_duration = chunk_duration

        # Load or create master ontology
        if os.path.exists(ontology_path):
            self.master_ontology = MasterClipOntology.load_binary(ontology_path)
            print(f"Loaded ontology: {self.master_ontology.videos_analyzed} videos, "
                  f"{self.master_ontology.total_clips_analyzed} clips")
        else:
            self.master_ontology = MasterClipOntology()
            print("Created new master ontology")

    def process_video(self, video_path: str, output_dir: str = None) -> Dict[str, Any]:
        """
        Process a video in parallel chunks.
        """
        print(f"\n{'='*60}")
        print("PARALLEL VIDEO PROCESSOR")
        print(f"{'='*60}")
        print(f"Video: {video_path}")
        print(f"Model: {self.model}")
        print(f"Workers: {self.max_workers}")
        print(f"Chunk size: {self.chunk_duration}s")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video not found: {video_path}")

        if output_dir is None:
            output_dir = os.path.dirname(video_path) or '.'

        # Create temp directory for chunks
        temp_dir = tempfile.mkdtemp(prefix="ontology_chunks_")

        try:
            # Split video into chunks
            chunks = split_video_into_chunks(
                video_path,
                self.chunk_duration,
                temp_dir
            )

            # Process chunks in parallel
            print(f"\nProcessing {len(chunks)} chunks with {self.max_workers} workers...")
            chunk_results = []

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all chunks
                future_to_chunk = {
                    executor.submit(
                        process_single_chunk,
                        chunk,
                        self.model,
                        i % self.max_workers
                    ): chunk
                    for i, chunk in enumerate(chunks)
                }

                # Collect results as they complete
                for future in as_completed(future_to_chunk):
                    chunk = future_to_chunk[future]
                    try:
                        result = future.result()
                        chunk_results.append(result)
                    except Exception as e:
                        print(f"Chunk {chunk.chunk_index} exception: {e}")
                        chunk_results.append(ChunkResult(
                            chunk_index=chunk.chunk_index,
                            start_offset=chunk.start_offset,
                            clips=[],
                            transcript='',
                            success=False,
                            error=str(e)
                        ))

            # Assemble results
            print("\nAssembling results...")
            annotated_clips, full_transcript = assemble_results(
                chunk_results, self.master_ontology
            )

            # Update counts
            self.master_ontology.videos_analyzed += 1

            # Generate output
            text_path = self._generate_output(
                video_path, annotated_clips, full_transcript, output_dir
            )

            # Save ontology
            ontology_text_path = self.ontology_path.replace('.pkl', '.txt')
            self.master_ontology.save(ontology_text_path)
            self.master_ontology.save_binary(self.ontology_path)

            # Summary
            successful_chunks = sum(1 for r in chunk_results if r.success)
            failed_chunks = len(chunk_results) - successful_chunks

            print(f"\n{'='*60}")
            print("COMPLETE")
            print(f"{'='*60}")
            print(f"Chunks: {successful_chunks}/{len(chunks)} successful")
            if failed_chunks > 0:
                print(f"Failed chunks: {failed_chunks}")
            print(f"Total clips: {len(annotated_clips)}")
            print(f"Output: {text_path}")
            print(f"Ontology: {ontology_text_path}")

            return {
                "video": video_path,
                "chunks_total": len(chunks),
                "chunks_successful": successful_chunks,
                "clips_count": len(annotated_clips),
                "output": text_path
            }

        finally:
            # Cleanup temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _generate_output(
        self,
        video_path: str,
        annotated_clips: List[AnnotatedClip],
        full_transcript: str,
        output_dir: str
    ) -> str:
        """Generate text output file."""
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        text_path = os.path.join(output_dir, f"{base_name}_ontology_{timestamp}.txt")

        lines = []
        lines.append("=" * 70)
        lines.append("VIDEO CLIP ONTOLOGY ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"Video: {os.path.basename(video_path)}")
        lines.append(f"Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Clips: {len(annotated_clips)}")
        lines.append("")

        lines.append("=" * 70)
        lines.append("FULL TRANSCRIPT")
        lines.append("=" * 70)
        lines.append(full_transcript or '[No transcript]')
        lines.append("")

        lines.append("=" * 70)
        lines.append("CLIP-BY-CLIP ONTOLOGY")
        lines.append("=" * 70)

        for clip in annotated_clips:
            lines.append(clip.to_text())

        lines.append("=" * 70)

        with open(text_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return text_path


def find_videos(directory: str) -> List[str]:
    """Find all video files in directory."""
    import glob
    extensions = ['.mp4', '.mov', '.webm', '.avi', '.mkv']
    videos = []
    for ext in extensions:
        videos.extend(glob.glob(os.path.join(directory, f'*{ext}')))
        videos.extend(glob.glob(os.path.join(directory, f'*{ext.upper()}')))
    return sorted(list(set(videos)))


def process_single_video_standalone(
    video_path: str,
    output_dir: str,
    model: str,
    chunk_duration: int,
    video_index: int,
    total_videos: int
) -> Dict[str, Any]:
    """
    Process a single video completely (with internal chunk parallelization).
    This function is called in parallel for multiple videos.
    Returns results dict for later aggregation.
    """
    video_name = os.path.basename(video_path)
    print(f"\n[Video {video_index}/{total_videos}] START: {video_name}")

    try:
        # Get video duration and split into chunks
        total_duration = get_video_duration(video_path)

        # Create temp directory for this video's chunks
        temp_dir = tempfile.mkdtemp(prefix=f"chunks_{video_index}_")

        try:
            # Split video
            chunks = split_video_into_chunks(video_path, chunk_duration, temp_dir)
            print(f"[Video {video_index}] Split into {len(chunks)} chunks")

            # Process chunks in parallel (within this video)
            chunk_results = []
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_to_chunk = {
                    executor.submit(
                        process_single_chunk,
                        chunk,
                        model,
                        video_index * 100 + i  # Unique thread ID
                    ): chunk
                    for i, chunk in enumerate(chunks)
                }

                for future in as_completed(future_to_chunk):
                    chunk = future_to_chunk[future]
                    try:
                        result = future.result()
                        chunk_results.append(result)
                    except Exception as e:
                        print(f"[Video {video_index}] Chunk {chunk.chunk_index} failed: {e}")
                        chunk_results.append(ChunkResult(
                            chunk_index=chunk.chunk_index,
                            start_offset=chunk.start_offset,
                            clips=[],
                            transcript='',
                            success=False,
                            error=str(e)
                        ))

            # Sort results by chunk index
            sorted_results = sorted(chunk_results, key=lambda r: r.chunk_index)

            # Collect all clips and transcripts
            all_clips = []
            transcript_parts = []
            all_clip_data = []

            for result in sorted_results:
                if result.success:
                    all_clips.extend(result.clips)
                    if result.transcript:
                        transcript_parts.append(result.transcript)
                else:
                    transcript_parts.append(f"[Chunk {result.chunk_index} failed]")

            # Renumber clips and build clip data
            for i, clip in enumerate(all_clips, 1):
                clip.clip_number = i
                clip_data = {
                    'visual': {
                        'shot_type': clip.ontology.shot_type,
                        'camera_angle': clip.ontology.camera_angle,
                        'camera_movement': clip.ontology.camera_movement,
                        'subject_type': clip.ontology.subject_type,
                        'subject_action': clip.ontology.subject_action,
                        'setting_type': clip.ontology.setting_type,
                        'lighting_style': clip.ontology.lighting_style,
                        'color_mood': clip.ontology.color_mood,
                        'text_purpose': clip.ontology.text_purpose,
                        'subject_description': clip.ontology.subject_description,
                        'setting_description': clip.ontology.setting_description,
                        'text_on_screen': clip.ontology.text_on_screen,
                    },
                    'emotional': {
                        'primary_emotion': clip.ontology.primary_emotion,
                        'secondary_emotion': clip.ontology.secondary_emotion,
                        'emotional_intensity': clip.ontology.emotional_intensity,
                    },
                    'functional': {
                        'clip_function': clip.ontology.clip_function,
                        'narrative_role': clip.ontology.narrative_role,
                        'persuasion_mechanism': clip.ontology.persuasion_mechanism,
                    },
                    'script_segment': clip.ontology.script_segment,
                    'duration_seconds': clip.ontology.duration_seconds,
                }
                all_clip_data.append(clip_data)

            full_transcript = ' '.join(transcript_parts)

            # Generate output file
            if output_dir is None:
                output_dir = os.path.dirname(video_path) or '.'

            base_name = os.path.splitext(os.path.basename(video_path))[0]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            text_path = os.path.join(output_dir, f"{base_name}_ontology_{timestamp}.txt")

            lines = []
            lines.append("=" * 70)
            lines.append("VIDEO CLIP ONTOLOGY ANALYSIS")
            lines.append("=" * 70)
            lines.append(f"Video: {os.path.basename(video_path)}")
            lines.append(f"Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"Total Clips: {len(all_clips)}")
            lines.append("")
            lines.append("=" * 70)
            lines.append("FULL TRANSCRIPT")
            lines.append("=" * 70)
            lines.append(full_transcript or '[No transcript]')
            lines.append("")
            lines.append("=" * 70)
            lines.append("CLIP-BY-CLIP ONTOLOGY")
            lines.append("=" * 70)

            for clip in all_clips:
                lines.append(clip.to_text())

            lines.append("=" * 70)

            with open(text_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))

            successful_chunks = sum(1 for r in chunk_results if r.success)
            print(f"[Video {video_index}/{total_videos}] DONE: {video_name} - "
                  f"{len(all_clips)} clips, {successful_chunks}/{len(chunks)} chunks OK")

            return {
                'video': video_path,
                'success': True,
                'clips_count': len(all_clips),
                'clips': all_clips,
                'clip_data': all_clip_data,
                'output': text_path,
                'chunks_total': len(chunks),
                'chunks_successful': successful_chunks,
            }

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print(f"[Video {video_index}/{total_videos}] FAILED: {video_name} - {e}")
        import traceback
        traceback.print_exc()
        return {
            'video': video_path,
            'success': False,
            'error': str(e),
            'clips_count': 0,
            'clip_data': [],
        }


def process_directory_parallel(
    video_dir: str,
    output_dir: str = None,
    model: str = "pro",
    ontology_path: str = "master_clip_ontology.pkl",
    max_video_workers: int = 3,
    chunk_duration: int = CHUNK_DURATION,
    synthesize_brain: bool = True
):
    """
    Process all videos in a directory in parallel.
    Each video is processed in parallel, and chunks within each video are also parallel.
    """
    videos = find_videos(video_dir)
    if not videos:
        print(f"No video files found in: {video_dir}")
        return

    if output_dir is None:
        output_dir = video_dir
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 70)
    print("PARALLEL VIDEO BATCH PROCESSOR")
    print("=" * 70)
    print(f"Videos found: {len(videos)}")
    print(f"Video workers: {max_video_workers} (parallel videos)")
    print(f"Chunk workers: 4 per video")
    print(f"Chunk size: {chunk_duration}s")
    print(f"Model: {model}")
    print(f"Output: {output_dir}")
    print("=" * 70)

    # Process videos in parallel
    all_results = []

    with ThreadPoolExecutor(max_workers=max_video_workers) as executor:
        future_to_video = {
            executor.submit(
                process_single_video_standalone,
                video_path,
                output_dir,
                model,
                chunk_duration,
                i,
                len(videos)
            ): video_path
            for i, video_path in enumerate(videos, 1)
        }

        for future in as_completed(future_to_video):
            video_path = future_to_video[future]
            try:
                result = future.result()
                all_results.append(result)
            except Exception as e:
                print(f"Video failed: {video_path} - {e}")
                all_results.append({
                    'video': video_path,
                    'success': False,
                    'error': str(e),
                    'clips_count': 0,
                    'clip_data': [],
                })

    # Now aggregate all results into master ontology
    print("\n" + "=" * 70)
    print("AGGREGATING RESULTS")
    print("=" * 70)

    # Load or create ontology
    if os.path.exists(ontology_path):
        master_ontology = MasterClipOntology.load_binary(ontology_path)
    else:
        master_ontology = MasterClipOntology()

    successful_videos = 0
    total_clips = 0

    for result in all_results:
        if result.get('success'):
            successful_videos += 1
            total_clips += result.get('clips_count', 0)

            # Update ontology from clips
            for clip in result.get('clips', []):
                master_ontology.update_from_clip(clip.ontology)

            master_ontology.videos_analyzed += 1

    # Save ontology
    ontology_text_path = ontology_path.replace('.pkl', '.txt')
    master_ontology.save(ontology_text_path)
    master_ontology.save_binary(ontology_path)

    # Final summary
    print("\n" + "=" * 70)
    print("BATCH COMPLETE")
    print("=" * 70)
    print(f"Videos processed: {successful_videos}/{len(videos)}")
    print(f"Total clips: {total_clips}")
    print(f"Ontology: {ontology_text_path}")
    print(f"Master ontology now has: {master_ontology.total_clips_analyzed} clips "
          f"from {master_ontology.videos_analyzed} videos")
    print("=" * 70)

    # Synthesize brain from all ontologies
    if synthesize_brain and successful_videos > 0:
        print("\n" + "=" * 70)
        print("SYNTHESIZING BRAIN")
        print("=" * 70)
        print("Analyzing all ontologies to create master playbook...")

        try:
            from brain_synthesizer import find_ontology_files, read_ontology_files, synthesize_brain as run_synthesis

            ontology_files = find_ontology_files(output_dir)
            if ontology_files:
                print(f"Found {len(ontology_files)} ontology files")
                ontologies_text = read_ontology_files(ontology_files)

                brain_output_path = os.path.join(output_dir, 'script_clip_brain.txt')
                run_synthesis(ontologies_text, brain_output_path)

                print(f"Brain saved to: {brain_output_path}")
            else:
                print("No ontology files found for brain synthesis")
        except Exception as e:
            print(f"Brain synthesis failed: {e}")
            print("You can run it manually: python brain_synthesizer.py <output_dir>")

    # List any failures
    failed = [r for r in all_results if not r.get('success')]
    if failed:
        print("\nFAILED VIDEOS:")
        for r in failed:
            print(f"  {r['video']}: {r.get('error', 'Unknown error')}")


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Process videos in parallel (both videos and chunks)"
    )
    parser.add_argument('video_path', help='Path to video file or directory')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--model', '-m', choices=['pro', 'flash'], default='pro')
    parser.add_argument('--video-workers', '-vw', type=int, default=3,
                        help='Number of videos to process in parallel (default: 3)')
    parser.add_argument('--chunk-size', '-c', type=int, default=40,
                        help='Chunk duration in seconds (default: 40)')
    parser.add_argument('--ontology', default='master_clip_ontology.pkl',
                        help='Path to ontology file')
    parser.add_argument('--no-brain', action='store_true',
                        help='Skip brain synthesis step')

    args = parser.parse_args()

    if not Config.GOOGLE_API_KEY:
        print("ERROR: GOOGLE_API_KEY not configured")
        sys.exit(1)

    # Check if path is a directory or file
    if os.path.isdir(args.video_path):
        # Parallel batch processing
        process_directory_parallel(
            video_dir=args.video_path,
            output_dir=args.output,
            model=args.model,
            ontology_path=args.ontology,
            max_video_workers=args.video_workers,
            chunk_duration=args.chunk_size,
            synthesize_brain=not args.no_brain
        )
    else:
        # Single video - use existing processor
        processor = ParallelVideoProcessor(
            model=args.model,
            ontology_path=args.ontology,
            max_workers=4,
            chunk_duration=args.chunk_size
        )
        try:
            processor.process_video(args.video_path, args.output)
        except Exception as e:
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
