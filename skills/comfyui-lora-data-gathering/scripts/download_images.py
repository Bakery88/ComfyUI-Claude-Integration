#!/usr/bin/env python3
"""Download images from a list of URLs, with deduplication and minimum resolution filtering."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def get_image_size(filepath):
    """Get image dimensions using Python's built-in imghdr or PIL if available."""
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            return img.size  # (width, height)
    except ImportError:
        # Fallback: try to read dimensions from file header
        # This is a rough fallback — PIL is strongly recommended
        return None


def file_hash(filepath):
    """Compute SHA-256 hash of a file for deduplication."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_file(url, output_path):
    """Download a file using curl."""
    try:
        result = subprocess.run(
            ["curl", "-sL", "-o", str(output_path),
             "-w", "%{http_code}",
             "--max-time", "30",
             "--retry", "2",
             url],
            capture_output=True, text=True, timeout=60
        )
        status_code = result.stdout.strip()
        if status_code.startswith("2") and output_path.exists() and output_path.stat().st_size > 0:
            return True
        else:
            output_path.unlink(missing_ok=True)
            return False
    except (subprocess.TimeoutExpired, Exception) as e:
        print(f"  Error downloading {url}: {e}", file=sys.stderr)
        output_path.unlink(missing_ok=True)
        return False


def main():
    parser = argparse.ArgumentParser(description="Download images from URL list")
    parser.add_argument("--urls-file", required=True, help="JSON file with image URLs (list of strings or sources.json format)")
    parser.add_argument("--output-dir", required=True, help="Directory to save downloaded images")
    parser.add_argument("--min-resolution", type=int, default=512, help="Minimum width/height in pixels (default: 512)")
    parser.add_argument("--start-index", type=int, default=1, help="Starting index for file numbering")
    parser.add_argument("--tier", type=str, default=None, help="Only download URLs matching this tier (A, B, or C)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse URLs file — supports both flat list and sources.json format
    with open(args.urls_file, "r") as f:
        data = json.load(f)

    urls = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                urls.append({"url": item, "source": item})
            elif isinstance(item, dict) and "url" in item:
                urls.append(item)
    elif isinstance(data, dict) and "urls" in data:
        urls = [{"url": u, "source": u} if isinstance(u, str) else u for u in data["urls"]]

    # Filter by tier if specified
    if args.tier:
        urls = [u for u in urls if u.get("tier", "").upper() == args.tier.upper()]

    if not urls:
        print("No URLs found in input file." + (f" (filter: tier {args.tier})" if args.tier else ""), file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(urls)} URLs..." + (f" (tier {args.tier})" if args.tier else ""))

    seen_hashes = set()
    download_log = []
    index = args.start_index
    downloaded = 0
    skipped_resolution = 0
    skipped_duplicate = 0
    failed = 0

    for entry in urls:
        url = entry["url"]
        source = entry.get("source", url)
        ext = Path(urlparse(url).path).suffix.lower()
        if ext not in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"):
            ext = ".png"  # Default extension

        temp_path = output_dir / f"_temp_download{ext}"
        print(f"  Downloading: {url[:80]}...")

        if not download_file(url, temp_path):
            failed += 1
            continue

        # Check for duplicates
        fhash = file_hash(temp_path)
        if fhash in seen_hashes:
            print(f"    Skipped (duplicate)")
            temp_path.unlink()
            skipped_duplicate += 1
            continue
        seen_hashes.add(fhash)

        # Check resolution
        size = get_image_size(temp_path)
        if size is not None:
            w, h = size
            if w < args.min_resolution or h < args.min_resolution:
                print(f"    Skipped (too small: {w}x{h})")
                temp_path.unlink()
                skipped_resolution += 1
                continue

        # Rename to sequential number
        final_name = f"{index:03d}{ext}"
        final_path = output_dir / final_name
        temp_path.rename(final_path)

        download_log.append({
            "filename": final_name,
            "source_url": url,
            "source_page": source,
            "hash": fhash,
            "resolution": f"{size[0]}x{size[1]}" if size else "unknown"
        })

        index += 1
        downloaded += 1
        print(f"    Saved as {final_name}" + (f" ({size[0]}x{size[1]})" if size else ""))

    # Write download log
    log_path = output_dir.parent / "download-log.json"
    with open(log_path, "w") as f:
        json.dump({"images": download_log}, f, indent=2)

    print(f"\nDone: {downloaded} downloaded, {skipped_resolution} too small, {skipped_duplicate} duplicates, {failed} failed")
    print(f"Download log: {log_path}")


if __name__ == "__main__":
    main()
