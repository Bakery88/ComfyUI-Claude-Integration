#!/usr/bin/env python3
"""Auto-caption images for LoRA training using Florence-2, WD14 Tagger, or BLIP-2."""

import argparse
import json
import sys
from pathlib import Path


def caption_with_florence2(image_path, trigger_word, mode, strip_words=None):
    """Generate caption using Florence-2 model."""
    try:
        from transformers import AutoProcessor, AutoModelForCausalLM
        from PIL import Image
        import torch
    except ImportError:
        print("Error: transformers and torch required. Install with:", file=sys.stderr)
        print("  pip install transformers torch Pillow", file=sys.stderr)
        sys.exit(1)

    # Lazy-load model (cached after first call)
    if not hasattr(caption_with_florence2, "_model"):
        model_id = "microsoft/Florence-2-base"
        print(f"Loading Florence-2 model ({model_id})...")
        caption_with_florence2._processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
        caption_with_florence2._model = AutoModelForCausalLM.from_pretrained(
            model_id, trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        )
        if torch.cuda.is_available():
            caption_with_florence2._model = caption_with_florence2._model.cuda()

    model = caption_with_florence2._model
    processor = caption_with_florence2._processor
    device = next(model.parameters()).device

    image = Image.open(image_path).convert("RGB")

    # Use DETAILED_CAPTION task for rich descriptions
    task = "<MORE_DETAILED_CAPTION>"
    inputs = processor(text=task, images=image, return_tensors="pt").to(device)

    with __import__("torch").no_grad():
        generated_ids = model.generate(
            **inputs, max_new_tokens=150, num_beams=3,
        )

    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # Remove the task prefix if present
    caption = caption.replace(task, "").strip()

    return format_caption(caption, trigger_word, mode, strip_words)


def caption_with_wd14(image_path, trigger_word, mode, strip_words=None):
    """Generate tags using WD14 Tagger (SmilingWolf's models via huggingface_hub)."""
    try:
        import onnxruntime as ort
        from PIL import Image
        import numpy as np
    except ImportError:
        print("Error: onnxruntime, Pillow, numpy required. Install with:", file=sys.stderr)
        print("  pip install onnxruntime Pillow numpy", file=sys.stderr)
        sys.exit(1)

    model_repo = "SmilingWolf/wd-swinv2-tagger-v3"
    model_dir = Path.home() / ".cache" / "wd14-tagger"
    model_path = model_dir / "model.onnx"
    tags_path = model_dir / "selected_tags.csv"

    # Download model if not cached
    if not model_path.exists() or not tags_path.exists():
        try:
            from huggingface_hub import hf_hub_download
        except ImportError:
            print("Error: huggingface_hub required for WD14 model download. Install with:", file=sys.stderr)
            print("  pip install huggingface_hub", file=sys.stderr)
            sys.exit(1)

        print(f"Downloading WD14 model from {model_repo}...")
        model_dir.mkdir(parents=True, exist_ok=True)
        hf_hub_download(model_repo, "model.onnx", local_dir=str(model_dir))
        hf_hub_download(model_repo, "selected_tags.csv", local_dir=str(model_dir))

    # Load model (cached after first call)
    if not hasattr(caption_with_wd14, "_session"):
        print("Loading WD14 tagger model...")
        import csv
        caption_with_wd14._session = ort.InferenceSession(str(model_path))
        with open(tags_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            caption_with_wd14._tags = [row[1] for row in reader]  # tag names in column 1

    session = caption_with_wd14._session
    tags = caption_with_wd14._tags

    # Preprocess image to 448x448 as expected by SwinV2 model
    image = Image.open(image_path).convert("RGB")
    image = image.resize((448, 448), Image.LANCZOS)
    img_array = np.array(image, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # add batch dim

    # Run inference
    input_name = session.get_inputs()[0].name
    output = session.run(None, {input_name: img_array})
    scores = output[0][0]

    # Collect tags above threshold
    threshold = 0.35
    tag_results = [(tags[i], scores[i]) for i in range(len(scores)) if scores[i] > threshold]
    tag_results.sort(key=lambda x: x[1], reverse=True)

    caption = ", ".join(tag for tag, _score in tag_results[:30])  # top 30 tags
    if not caption:
        caption = "illustration"

    return format_caption(caption, trigger_word, mode, strip_words)


def caption_with_blip2(image_path, trigger_word, mode, strip_words=None):
    """Generate caption using BLIP-2 model."""
    try:
        from transformers import Blip2Processor, Blip2ForConditionalGeneration
        from PIL import Image
        import torch
    except ImportError:
        print("Error: transformers and torch required. Install with:", file=sys.stderr)
        print("  pip install transformers torch Pillow", file=sys.stderr)
        sys.exit(1)

    if not hasattr(caption_with_blip2, "_model"):
        model_id = "Salesforce/blip2-opt-2.7b"
        print(f"Loading BLIP-2 model ({model_id})...")
        caption_with_blip2._processor = Blip2Processor.from_pretrained(model_id)
        caption_with_blip2._model = Blip2ForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=__import__("torch").float16 if torch.cuda.is_available() else __import__("torch").float32,
        )
        if torch.cuda.is_available():
            caption_with_blip2._model = caption_with_blip2._model.cuda()

    model = caption_with_blip2._model
    processor = caption_with_blip2._processor
    device = next(model.parameters()).device

    image = Image.open(image_path).convert("RGB")
    inputs = processor(images=image, return_tensors="pt").to(device)

    with __import__("torch").no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=100)

    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    return format_caption(caption, trigger_word, mode, strip_words)


DEFAULT_STRIP_WORDS = [
    # Style-describing terms
    "watercolor", "oil painting", "anime style", "pixel art", "digital art",
    "cel-shaded", "cel shaded", "3d render", "3d rendering", "cgi",
    "concept art", "fan art", "fanart",
    # Medium descriptors
    "painting", "illustration", "photograph", "photography", "drawing",
    "sketch", "artwork", "print",
    # Quality/aesthetic words
    "beautiful", "masterpiece", "high quality", "high-quality", "stunning",
    "gorgeous", "amazing", "incredible", "breathtaking", "magnificent",
    "best quality", "ultra detailed", "highly detailed",
]


def clean_caption(caption, strip_words):
    """Remove style-leaking and quality words from a caption.

    These words describe *how* the image was made rather than *what's in it*.
    Leaving them in weakens the LoRA by teaching it to associate the trigger
    word with text tokens instead of visual features.
    """
    cleaned = caption
    for word in strip_words:
        # Case-insensitive removal, handling commas and extra spaces
        import re
        pattern = re.compile(r',?\s*\b' + re.escape(word) + r'\b\s*,?', re.IGNORECASE)
        cleaned = pattern.sub(', ', cleaned)
    # Clean up leftover punctuation artifacts
    cleaned = re.sub(r',\s*,', ',', cleaned)  # double commas
    cleaned = re.sub(r'^\s*,\s*', '', cleaned)  # leading comma
    cleaned = re.sub(r'\s*,\s*$', '', cleaned)  # trailing comma
    cleaned = re.sub(r'\s{2,}', ' ', cleaned)  # double spaces
    return cleaned.strip()


def format_caption(raw_caption, trigger_word, mode, strip_words=None):
    """Format caption according to LoRA training conventions, with hygiene filtering."""
    raw_caption = raw_caption.strip().rstrip(".")

    if strip_words:
        raw_caption = clean_caption(raw_caption, strip_words)

    if mode == "style":
        return f"{trigger_word} style, {raw_caption}"
    elif mode == "subject":
        return f"{trigger_word}, {raw_caption}"
    elif mode == "object":
        return f"{trigger_word}, {raw_caption}"
    else:
        return f"{trigger_word}, {raw_caption}"


CAPTIONERS = {
    "florence2": caption_with_florence2,
    "blip2": caption_with_blip2,
    "wd14": caption_with_wd14,
}


def main():
    parser = argparse.ArgumentParser(description="Auto-caption images for LoRA training")
    parser.add_argument("--image-dir", required=True, help="Directory with images to caption")
    parser.add_argument("--output-dir", help="Directory for caption files (default: same as image-dir)")
    parser.add_argument("--trigger-word", required=True, help="Trigger word for the LoRA")
    parser.add_argument("--mode", required=True, choices=["style", "subject", "object"],
                        help="Captioning mode: style, subject, or object")
    parser.add_argument("--captioner", default="florence2", choices=list(CAPTIONERS.keys()),
                        help="Captioning model to use (default: florence2)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing caption files")
    parser.add_argument("--extra-strip-words", default="",
                        help="Comma-separated list of additional words to strip from captions (project-specific style leaks)")
    args = parser.parse_args()

    # Build the full strip word list
    strip_words = list(DEFAULT_STRIP_WORDS)
    if args.extra_strip_words:
        strip_words.extend(w.strip() for w in args.extra_strip_words.split(",") if w.strip())

    image_dir = Path(args.image_dir)
    output_dir = Path(args.output_dir) if args.output_dir else image_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    images = sorted([f for f in image_dir.iterdir() if f.suffix.lower() in image_extensions])

    if not images:
        print(f"No images found in {image_dir}", file=sys.stderr)
        sys.exit(1)

    caption_fn = CAPTIONERS[args.captioner]
    print(f"Captioning {len(images)} images with {args.captioner} (mode: {args.mode}, trigger: '{args.trigger_word}')")

    captions = []
    for img_path in images:
        caption_path = output_dir / f"{img_path.stem}.txt"

        if caption_path.exists() and not args.overwrite:
            print(f"  {img_path.name}: caption exists, skipping (use --overwrite to replace)")
            existing = caption_path.read_text(encoding="utf-8").strip()
            captions.append({"filename": img_path.name, "caption": existing, "source": "existing"})
            continue

        try:
            caption = caption_fn(img_path, args.trigger_word, args.mode, strip_words)
            caption_path.write_text(caption, encoding="utf-8")
            captions.append({"filename": img_path.name, "caption": caption, "source": args.captioner})
            print(f"  {img_path.name}: {caption[:80]}{'...' if len(caption) > 80 else ''}")
        except Exception as e:
            print(f"  {img_path.name}: ERROR - {e}", file=sys.stderr)
            captions.append({"filename": img_path.name, "caption": None, "source": "error", "error": str(e)})

    # Write caption report
    report = {
        "captioner": args.captioner,
        "mode": args.mode,
        "trigger_word": args.trigger_word,
        "total": len(images),
        "captioned": sum(1 for c in captions if c.get("caption")),
        "captions": captions,
    }

    report_path = output_dir / "caption-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    captioned = report["captioned"]
    print(f"\nDone: {captioned}/{len(images)} images captioned")
    print(f"Report: {report_path}")

    # Show a few example captions for review
    print("\n--- Example captions (first 3) ---")
    for c in captions[:3]:
        if c.get("caption"):
            print(f"  {c['filename']}: {c['caption']}")


if __name__ == "__main__":
    main()
