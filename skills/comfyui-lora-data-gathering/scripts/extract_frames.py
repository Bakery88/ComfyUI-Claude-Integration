#!/usr/bin/env python3
"""Extract frames from videos at regular intervals with deduplication and quality filtering."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            capture_output=True, text=True, timeout=30
        )
        return float(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, Exception):
        return None


def extract_frame_at(video_path, timestamp, output_path):
    """Extract a single frame at a given timestamp."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-ss", str(timestamp), "-i", str(video_path),
             "-vframes", "1", "-q:v", "2", str(output_path)],
            capture_output=True, text=True, timeout=30
        )
        return output_path.exists() and output_path.stat().st_size > 0
    except (subprocess.TimeoutExpired, Exception):
        return False


def image_hash(filepath):
    """Simple file hash for deduplication."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def check_image_quality(filepath, min_resolution):
    """Check if image meets minimum quality requirements."""
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            w, h = img.size
            if w < min_resolution or h < min_resolution:
                return False, f"too small ({w}x{h})"

            # Check if image is mostly black or white (transitions/fades)
            grayscale = img.convert("L")
            pixels = list(grayscale.getdata())
            avg_brightness = sum(pixels) / len(pixels)
            if avg_brightness < 15:
                return False, "mostly black (likely transition)"
            if avg_brightness > 245:
                return False, "mostly white (likely transition)"

            return True, f"{w}x{h}"
    except ImportError:
        # Without PIL, skip quality checks beyond file size
        return True, "unknown (PIL not available)"
    except Exception as e:
        return False, f"error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Extract frames from videos for LoRA training")
    parser.add_argument("--video-dir", required=True, help="Directory containing video files")
    parser.add_argument("--output-dir", required=True, help="Directory to save extracted frames")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between frame captures (default: 2.0)")
    parser.add_argument("--min-resolution", type=int, default=512, help="Minimum frame width/height (default: 512)")
    parser.add_argument("--max-frames", type=int, default=100, help="Maximum total frames to extract across all videos (default: 100)")
    parser.add_argument("--start-index", type=int, default=1, help="Starting index for file numbering (set this to continue from Step 2 downloads)")
    args = parser.parse_args()

    video_dir = Path(args.video_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Check ffmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=10)
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install it from https://ffmpeg.org", file=sys.stderr)
        sys.exit(1)

    video_extensions = {".mp4", ".mkv", ".webm", ".avi", ".mov", ".flv"}
    videos = [f for f in video_dir.iterdir() if f.suffix.lower() in video_extensions]

    if not videos:
        print(f"No video files found in {video_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(videos)} video(s)")

    index = args.start_index
    seen_hashes = set()
    total_extracted = 0
    total_skipped = 0
    extraction_log = []

    max_reached = False
    for video_path in sorted(videos):
        if max_reached:
            print(f"\nSkipping {video_path.name} (max frames reached)")
            continue

        print(f"\nProcessing: {video_path.name}")

        duration = get_video_duration(video_path)
        if duration is None:
            print(f"  Could not determine duration, skipping")
            continue

        num_frames = int(duration / args.interval)
        print(f"  Duration: {duration:.1f}s, extracting up to {num_frames} frames at {args.interval}s intervals")

        video_extracted = 0
        video_skipped = 0

        for i in range(num_frames):
            if total_extracted >= args.max_frames:
                print(f"  Reached max frame limit ({args.max_frames}), stopping extraction")
                max_reached = True
                break

            timestamp = i * args.interval
            temp_path = output_dir / f"_temp_frame.png"

            if not extract_frame_at(video_path, timestamp, temp_path):
                video_skipped += 1
                continue

            # Quality check
            quality_ok, quality_info = check_image_quality(temp_path, args.min_resolution)
            if not quality_ok:
                temp_path.unlink(missing_ok=True)
                video_skipped += 1
                continue

            # Deduplication (exact file hash — near-duplicates handled in curation)
            fhash = image_hash(temp_path)
            if fhash in seen_hashes:
                temp_path.unlink(missing_ok=True)
                video_skipped += 1
                continue
            seen_hashes.add(fhash)

            # Keep this frame
            final_name = f"{index:03d}.png"
            final_path = output_dir / final_name
            temp_path.rename(final_path)

            extraction_log.append({
                "filename": final_name,
                "source_video": video_path.name,
                "timestamp": round(timestamp, 1),
                "resolution": quality_info,
                "hash": fhash
            })

            index += 1
            video_extracted += 1

        total_extracted += video_extracted
        total_skipped += video_skipped
        print(f"  Extracted {video_extracted} frames, skipped {video_skipped}")

    # Write extraction log
    log_path = output_dir.parent / "extraction-log.json"
    with open(log_path, "w") as f:
        json.dump({"frames": extraction_log}, f, indent=2)

    print(f"\nDone: {total_extracted} frames extracted, {total_skipped} skipped")
    print(f"Extraction log: {log_path}")


if __name__ == "__main__":
    main()
