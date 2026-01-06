#!/usr/bin/env python3
"""
Smart Video Compressor
======================
Intelligently compresses videos by probing for easy wins:
- Downscale if resolution is higher than needed
- Re-encode if using inefficient codec
- Reduce bitrate if excessively high
- Strip unnecessary audio channels
- Remove metadata bloat

Target: under 20MB for Gemini API while maintaining quality.

Usage:
    python compress_videos.py /path/to/videos/
    python compress_videos.py video.mp4
    python compress_videos.py /path/to/videos/ --target-size 15
"""

import argparse
import os
import sys
import subprocess
import glob
import json
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class VideoInfo:
    """Probed video information."""
    path: str
    duration: float  # seconds
    file_size_mb: float

    # Video stream
    width: int
    height: int
    fps: float
    video_codec: str
    video_bitrate: Optional[int]  # kbps
    pixel_format: str

    # Audio stream
    audio_codec: Optional[str]
    audio_bitrate: Optional[int]  # kbps
    audio_channels: Optional[int]
    audio_sample_rate: Optional[int]

    # Calculated
    total_bitrate: int  # kbps

    def __str__(self):
        return (
            f"{os.path.basename(self.path)}\n"
            f"  Size: {self.file_size_mb:.1f}MB | Duration: {self.duration:.1f}s\n"
            f"  Video: {self.width}x{self.height} @ {self.fps:.1f}fps | {self.video_codec} | {self.video_bitrate or '?'}kbps\n"
            f"  Audio: {self.audio_codec or 'none'} | {self.audio_bitrate or '?'}kbps | {self.audio_channels or 0}ch"
        )


@dataclass
class CompressionPlan:
    """Plan for how to compress a video."""
    actions: List[str]
    target_width: Optional[int]
    target_height: Optional[int]
    target_video_bitrate: int  # kbps
    target_audio_bitrate: int  # kbps
    target_fps: Optional[float]
    estimated_size_mb: float
    reason: str


def probe_video(path: str) -> Optional[VideoInfo]:
    """Probe video file for detailed information."""
    cmd = [
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', '-show_streams',
        path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"  Error probing {path}: {e}")
        return None

    # Extract format info
    fmt = data.get('format', {})
    duration = float(fmt.get('duration', 0))
    file_size = int(fmt.get('size', 0))
    file_size_mb = file_size / (1024 * 1024)
    total_bitrate = int(fmt.get('bit_rate', 0)) // 1000  # to kbps

    # Find video and audio streams
    video_stream = None
    audio_stream = None

    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video' and not video_stream:
            video_stream = stream
        elif stream.get('codec_type') == 'audio' and not audio_stream:
            audio_stream = stream

    if not video_stream:
        print(f"  No video stream found in {path}")
        return None

    # Parse video info
    width = video_stream.get('width', 0)
    height = video_stream.get('height', 0)

    # Parse FPS from r_frame_rate (e.g., "30/1" or "30000/1001")
    fps_str = video_stream.get('r_frame_rate', '30/1')
    try:
        if '/' in fps_str:
            num, den = fps_str.split('/')
            fps = float(num) / float(den)
        else:
            fps = float(fps_str)
    except:
        fps = 30.0

    video_codec = video_stream.get('codec_name', 'unknown')
    video_bitrate = None
    if video_stream.get('bit_rate'):
        video_bitrate = int(video_stream['bit_rate']) // 1000

    pixel_format = video_stream.get('pix_fmt', 'unknown')

    # Parse audio info
    audio_codec = None
    audio_bitrate = None
    audio_channels = None
    audio_sample_rate = None

    if audio_stream:
        audio_codec = audio_stream.get('codec_name')
        if audio_stream.get('bit_rate'):
            audio_bitrate = int(audio_stream['bit_rate']) // 1000
        audio_channels = audio_stream.get('channels')
        audio_sample_rate = audio_stream.get('sample_rate')
        if audio_sample_rate:
            audio_sample_rate = int(audio_sample_rate)

    return VideoInfo(
        path=path,
        duration=duration,
        file_size_mb=file_size_mb,
        width=width,
        height=height,
        fps=fps,
        video_codec=video_codec,
        video_bitrate=video_bitrate,
        pixel_format=pixel_format,
        audio_codec=audio_codec,
        audio_bitrate=audio_bitrate,
        audio_channels=audio_channels,
        audio_sample_rate=audio_sample_rate,
        total_bitrate=total_bitrate
    )


def plan_compression(info: VideoInfo, target_size_mb: float = 18) -> CompressionPlan:
    """
    Analyze video and create optimal compression plan.
    Finds easy wins before aggressive compression.
    """
    actions = []

    target_height = None
    target_width = None
    target_fps = None

    # Current effective bitrate
    current_bitrate = info.total_bitrate or int((info.file_size_mb * 8 * 1024) / info.duration)

    # Calculate what bitrate we need for target size
    needed_bitrate = int((target_size_mb * 8 * 1024) / info.duration)

    # Start with current values
    planned_video_bitrate = info.video_bitrate or (current_bitrate - 128)
    planned_audio_bitrate = info.audio_bitrate or 128

    # === EASY WIN 1: Downscale high resolution ===
    # For Gemini analysis, we don't need 4K or even 1080p
    if info.height > 720:
        target_height = 720
        target_width = -2  # Maintain aspect ratio
        scale_factor = 720 / info.height
        # Bitrate can scale roughly with pixel count
        pixel_reduction = scale_factor ** 2
        planned_video_bitrate = int(planned_video_bitrate * pixel_reduction * 1.2)  # Keep some quality
        actions.append(f"Downscale {info.height}p → 720p (saves ~{int((1-pixel_reduction)*100)}% bitrate)")
    elif info.height > 480 and info.file_size_mb > target_size_mb * 1.5:
        # If still too big, consider 480p
        target_height = 480
        target_width = -2
        scale_factor = 480 / info.height
        pixel_reduction = scale_factor ** 2
        planned_video_bitrate = int(planned_video_bitrate * pixel_reduction * 1.2)
        actions.append(f"Downscale {info.height}p → 480p (aggressive)")

    # === EASY WIN 2: Reduce excessive FPS ===
    if info.fps > 30:
        target_fps = 30
        fps_reduction = 30 / info.fps
        planned_video_bitrate = int(planned_video_bitrate * (0.7 + 0.3 * fps_reduction))
        actions.append(f"Reduce FPS {info.fps:.0f} → 30 (saves ~{int((1-fps_reduction)*30)}% bitrate)")

    # === EASY WIN 3: Re-encode inefficient codecs ===
    inefficient_codecs = ['mpeg4', 'msmpeg4', 'wmv', 'mpeg2video', 'mjpeg', 'rawvideo']
    if info.video_codec.lower() in inefficient_codecs:
        # H.264 is much more efficient
        efficiency_gain = 0.5  # Can often halve the bitrate
        planned_video_bitrate = int(planned_video_bitrate * efficiency_gain)
        actions.append(f"Re-encode {info.video_codec} → H.264 (much more efficient)")
    elif info.video_codec.lower() not in ['h264', 'hevc', 'h265', 'vp9', 'av1']:
        actions.append(f"Re-encode {info.video_codec} → H.264")

    # === EASY WIN 4: Reduce excessive audio ===
    if info.audio_bitrate and info.audio_bitrate > 192:
        planned_audio_bitrate = 128
        actions.append(f"Reduce audio {info.audio_bitrate}kbps → 128kbps")
    elif info.audio_channels and info.audio_channels > 2:
        planned_audio_bitrate = 128
        actions.append(f"Downmix {info.audio_channels}ch → stereo")
    else:
        planned_audio_bitrate = min(info.audio_bitrate or 128, 128)

    # === Calculate if we need more aggressive compression ===
    estimated_bitrate = planned_video_bitrate + planned_audio_bitrate
    estimated_size = (estimated_bitrate * info.duration) / (8 * 1024)

    if estimated_size > target_size_mb:
        # Need to reduce video bitrate further
        available_for_video = needed_bitrate - planned_audio_bitrate
        available_for_video = max(available_for_video, 300)  # Minimum quality floor

        if available_for_video < planned_video_bitrate:
            reduction_pct = int((1 - available_for_video / planned_video_bitrate) * 100)
            actions.append(f"Reduce video bitrate by {reduction_pct}% to hit target")
            planned_video_bitrate = available_for_video

    # Recalculate estimated size
    final_bitrate = planned_video_bitrate + planned_audio_bitrate
    estimated_size = (final_bitrate * info.duration) / (8 * 1024)

    # Build reason string
    if not actions:
        reason = "Minor re-encode for compatibility"
        actions.append("Re-encode with optimized settings")
    else:
        reason = f"{len(actions)} optimizations identified"

    return CompressionPlan(
        actions=actions,
        target_width=target_width,
        target_height=target_height,
        target_video_bitrate=planned_video_bitrate,
        target_audio_bitrate=planned_audio_bitrate,
        target_fps=target_fps,
        estimated_size_mb=estimated_size,
        reason=reason
    )


def execute_compression(
    info: VideoInfo,
    plan: CompressionPlan,
    output_path: str
) -> bool:
    """Execute the compression plan."""

    filters = []

    # Scale filter
    if plan.target_height:
        filters.append(f"scale={plan.target_width}:{plan.target_height}")

    # FPS filter
    if plan.target_fps:
        filters.append(f"fps={plan.target_fps}")

    # Build ffmpeg command
    cmd = ['ffmpeg', '-y', '-i', info.path]

    # Video filters
    if filters:
        cmd.extend(['-vf', ','.join(filters)])

    # Video encoding
    cmd.extend([
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-b:v', f'{plan.target_video_bitrate}k',
        '-maxrate', f'{int(plan.target_video_bitrate * 1.5)}k',
        '-bufsize', f'{plan.target_video_bitrate * 2}k',
        '-pix_fmt', 'yuv420p',  # Compatibility
    ])

    # Audio encoding
    if info.audio_codec:
        cmd.extend([
            '-c:a', 'aac',
            '-b:a', f'{plan.target_audio_bitrate}k',
            '-ac', '2',  # Stereo
        ])
    else:
        cmd.extend(['-an'])  # No audio

    # Output
    cmd.extend([
        '-movflags', '+faststart',
        output_path
    ])

    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  FFmpeg error: {e.stderr.decode()[:500] if e.stderr else 'Unknown'}")
        return False


def process_video(
    input_path: str,
    output_path: str,
    target_size_mb: float = 18,
    verbose: bool = True
) -> bool:
    """Process a single video with smart compression."""

    # Probe
    info = probe_video(input_path)
    if not info:
        return False

    if verbose:
        print(info)

    # Check if already small enough
    if info.file_size_mb <= target_size_mb:
        print(f"  ✓ Already under {target_size_mb}MB - copying as-is")
        subprocess.run(['cp', input_path, output_path])
        return True

    # Plan compression
    plan = plan_compression(info, target_size_mb)

    if verbose:
        print(f"\n  Compression Plan ({plan.reason}):")
        for action in plan.actions:
            print(f"    • {action}")
        print(f"    → Estimated output: {plan.estimated_size_mb:.1f}MB")

    # Execute
    print(f"  Compressing...")
    success = execute_compression(info, plan, output_path)

    if success:
        new_size = os.path.getsize(output_path) / (1024 * 1024)
        reduction = ((info.file_size_mb - new_size) / info.file_size_mb) * 100
        status = "✓" if new_size <= target_size_mb else "⚠"
        print(f"  {status} Done: {info.file_size_mb:.1f}MB → {new_size:.1f}MB ({reduction:.0f}% smaller)")

        if new_size > target_size_mb:
            print(f"    Warning: Still over target. May need manual review.")

        return True
    else:
        print(f"  ✗ Compression failed")
        return False


def process_directory(
    input_dir: str,
    output_dir: str = None,
    target_size_mb: float = 18
):
    """Process all videos in a directory."""

    # Find videos
    extensions = ['.mp4', '.mov', '.webm', '.avi', '.mkv', '.MP4', '.MOV', '.MKV', '.AVI']
    videos = []
    for ext in extensions:
        videos.extend(glob.glob(os.path.join(input_dir, f'*{ext}')))
    videos = sorted(list(set(videos)))

    if not videos:
        print(f"No videos found in: {input_dir}")
        return

    # Setup output
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'compressed')
    os.makedirs(output_dir, exist_ok=True)

    print(f"{'='*60}")
    print(f"SMART VIDEO COMPRESSOR")
    print(f"{'='*60}")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Target: {target_size_mb}MB per video")
    print(f"Videos found: {len(videos)}")
    print(f"{'='*60}\n")

    results = {'success': 0, 'skipped': 0, 'failed': 0}

    for i, video_path in enumerate(videos, 1):
        filename = os.path.basename(video_path)
        name, _ = os.path.splitext(filename)
        output_path = os.path.join(output_dir, f"{name}.mp4")

        print(f"\n[{i}/{len(videos)}] {filename}")
        print("-" * 50)

        # Check if output already exists
        if os.path.exists(output_path):
            existing_size = os.path.getsize(output_path) / (1024 * 1024)
            if existing_size <= target_size_mb:
                print(f"  ✓ Already processed ({existing_size:.1f}MB)")
                results['skipped'] += 1
                continue

        if process_video(video_path, output_path, target_size_mb):
            results['success'] += 1
        else:
            results['failed'] += 1

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Compressed: {results['success']}")
    print(f"Skipped: {results['skipped']}")
    print(f"Failed: {results['failed']}")
    print(f"Output: {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Smart video compression for Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/videos/           # Compress directory
  %(prog)s video.mp4                  # Compress single file
  %(prog)s video.mp4 -o out.mp4       # Specify output
  %(prog)s /path/to/videos/ -s 15     # Target 15MB instead of 18MB
  %(prog)s video.mp4 --probe          # Just show video info
        """
    )

    parser.add_argument('input', help='Video file or directory')
    parser.add_argument('--output', '-o', help='Output file or directory')
    parser.add_argument('--target-size', '-s', type=float, default=18,
                        help='Target size in MB (default: 18)')
    parser.add_argument('--probe', '-p', action='store_true',
                        help='Just probe and show info, no compression')

    args = parser.parse_args()

    # Check ffmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: ffmpeg/ffprobe not found")
        print("Install: brew install ffmpeg")
        sys.exit(1)

    # Probe only mode
    if args.probe:
        if os.path.isdir(args.input):
            extensions = ['.mp4', '.mov', '.webm', '.avi', '.mkv']
            for ext in extensions:
                for path in glob.glob(os.path.join(args.input, f'*{ext}')):
                    info = probe_video(path)
                    if info:
                        print(info)
                        plan = plan_compression(info, args.target_size)
                        print(f"  Plan: {plan.reason}")
                        for action in plan.actions:
                            print(f"    • {action}")
                        print()
        else:
            info = probe_video(args.input)
            if info:
                print(info)
                plan = plan_compression(info, args.target_size)
                print(f"\nCompression Plan ({plan.reason}):")
                for action in plan.actions:
                    print(f"  • {action}")
                print(f"  → Estimated: {plan.estimated_size_mb:.1f}MB")
        return

    # Process
    if os.path.isdir(args.input):
        process_directory(args.input, args.output, args.target_size)
    else:
        if not os.path.exists(args.input):
            print(f"File not found: {args.input}")
            sys.exit(1)

        output = args.output
        if not output:
            name, _ = os.path.splitext(args.input)
            output = f"{name}_compressed.mp4"

        process_video(args.input, output, args.target_size)


if __name__ == "__main__":
    main()
