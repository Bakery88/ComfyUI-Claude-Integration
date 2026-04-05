#!/usr/bin/env python3
"""Prepare raw images for LoRA training: resize, crop, convert, and organize into resolution buckets."""

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)


# Standard resolution buckets for aspect-ratio-aware training
RESOLUTION_BUCKETS = {
    1024: [
        (1024, 1024), (1152, 896), (896, 1152),
        (1216, 832), (832, 1216), (1344, 768), (768, 1344),
        (1536, 640), (640, 1536),
    ],
    512: [
        (512, 512), (576, 448), (448, 576),
        (640, 384), (384, 640), (768, 320), (320, 768),
    ],
}


def find_best_bucket(width, height, target_resolution):
    """Find the resolution bucket that best matches the image's aspect ratio."""
    buckets = RESOLUTION_BUCKETS.get(target_resolution, [(target_resolution, target_resolution)])
    aspect = width / height

    best_bucket = None
    best_diff = float("inf")

    for bw, bh in buckets:
        bucket_aspect = bw / bh
        diff = abs(aspect - bucket_aspect)
        if diff < best_diff:
            best_diff = diff
            best_bucket = (bw, bh)

    return best_bucket


def smart_crop_resize(img, target_w, target_h):
    """Resize and crop image to target dimensions, keeping the most important region centered."""
    w, h = img.size
    target_aspect = target_w / target_h
    img_aspect = w / h

    if img_aspect > target_aspect:
        # Image is wider — crop sides
        new_w = int(h * target_aspect)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif img_aspect < target_aspect:
        # Image is taller — crop top/bottom
        new_h = int(w / target_aspect)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img.resize((target_w, target_h), Image.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description="Prepare images for LoRA training")
    parser.add_argument("--input-dir", required=True, help="Directory with raw images")
    parser.add_argument("--output-dir", required=True, help="Directory for processed images")
    parser.add_argument("--target-resolution", type=int, default=1024, choices=[512, 1024],
                        help="Target resolution (default: 1024)")
    parser.add_argument("--crop-mode", default="smart", choices=["smart", "center", "square"],
                        help="Cropping mode (default: smart)")
    parser.add_argument("--format", default="png", choices=["png", "jpg"],
                        help="Output format (default: png)")
    parser.add_argument("--keep-list", default=None,
                        help="Text file with filenames to process (one per line). If omitted, all images are processed.")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"}
    images = sorted([f for f in input_dir.iterdir() if f.suffix.lower() in image_extensions])

    # Filter to keep-list if provided
    if args.keep_list:
        keep_path = Path(args.keep_list)
        if not keep_path.exists():
            print(f"Error: keep-list file not found: {keep_path}", file=sys.stderr)
            sys.exit(1)
        keep_names = set(line.strip() for line in keep_path.read_text(encoding="utf-8").splitlines() if line.strip())
        before_count = len(images)
        images = [f for f in images if f.name in keep_names]
        print(f"Keep-list filter: {len(images)}/{before_count} images selected")

    if not images:
        print(f"No images found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Processing {len(images)} images at target resolution {args.target_resolution}px")

    processed = []
    bucket_counts = {}

    for i, img_path in enumerate(images, 1):
        try:
            with Image.open(img_path) as img:
                img = img.convert("RGB")
                w, h = img.size

                if args.crop_mode == "square":
                    target_w = target_h = args.target_resolution
                else:
                    target_w, target_h = find_best_bucket(w, h, args.target_resolution)

                # Warn if significant upscaling is needed
                scale_x = target_w / w
                scale_y = target_h / h
                max_scale = max(scale_x, scale_y)
                upscale_warning = None
                if max_scale > 2.0:
                    upscale_warning = f"WARNING: {img_path.name} needs {max_scale:.1f}x upscale ({w}x{h} -> {target_w}x{target_h}) — quality may suffer"
                    print(f"  {upscale_warning}")

                result = smart_crop_resize(img, target_w, target_h)

                out_ext = f".{args.format}"
                out_name = f"{i:03d}{out_ext}"
                out_path = output_dir / out_name

                save_kwargs = {"optimize": True}
                if args.format == "jpg":
                    save_kwargs["quality"] = 95

                result.save(out_path, **save_kwargs)

                bucket_key = f"{target_w}x{target_h}"
                bucket_counts[bucket_key] = bucket_counts.get(bucket_key, 0) + 1

                entry = {
                    "filename": out_name,
                    "original": img_path.name,
                    "original_resolution": f"{w}x{h}",
                    "output_resolution": bucket_key,
                }
                if upscale_warning:
                    entry["upscale_warning"] = upscale_warning
                processed.append(entry)

                # Copy caption file if it exists
                caption_src = img_path.with_suffix(".txt")
                if caption_src.exists():
                    caption_dst = out_path.with_suffix(".txt")
                    caption_dst.write_text(caption_src.read_text(encoding="utf-8"), encoding="utf-8")

                print(f"  {img_path.name} ({w}x{h}) -> {out_name} ({bucket_key})")

        except Exception as e:
            print(f"  Error processing {img_path.name}: {e}", file=sys.stderr)
            continue

    # Write processing report
    report = {
        "total_processed": len(processed),
        "target_resolution": args.target_resolution,
        "resolution_buckets": bucket_counts,
        "images": processed,
    }

    report_path = output_dir / "processing-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nDone: {len(processed)}/{len(images)} images processed")
    print(f"Resolution buckets: {bucket_counts}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
