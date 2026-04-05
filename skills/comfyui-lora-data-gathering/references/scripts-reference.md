# Scripts Reference

CLI flags, captioner details, and usage examples for all bundled scripts.

## Table of Contents

- [download_images.py](#download_imagespy)
- [extract_frames.py](#extract_framespy)
- [prepare_dataset.py](#prepare_datasetpy)
- [auto_caption.py](#auto_captionpy)
- [Captioner Comparison](#captioner-comparison)
- [Required External Tools](#required-external-tools)

---

## download_images.py

Downloads images from a URL list, with filtering and deduplication.

```bash
python scripts/download_images.py \
  --urls-file datasets/{project-name}/image-urls.json \
  --output-dir datasets/{project-name}/raw/ \
  --min-resolution 512 \
  --tier A \
  --start-index 1
```

| Flag | Required | Default | Description |
|---|---|---|---|
| `--urls-file` | Yes | — | Path to `image-urls.json` (from Step 2 Phase 1) |
| `--output-dir` | Yes | — | Directory for downloaded images |
| `--min-resolution` | No | 512 | Skip images smaller than this (width or height) |
| `--tier` | No | all | Download only URLs from this tier (`A`, `B`, or `C`) |
| `--start-index` | No | 1 | Starting number for sequential filenames (`001.png`, `002.png`...) |

**Outputs**:
- Sequential image files (`001.png`, `002.png`, ...)
- `download-log.json` — source attribution for each image

**Behaviors**:
- Skips images below minimum resolution
- Deduplicates by file hash (exact matches)
- Names files sequentially from `--start-index`

---

## extract_frames.py

Extracts frames from video files at regular intervals with quality filtering.

```bash
python scripts/extract_frames.py \
  --video-dir datasets/{project-name}/video/ \
  --output-dir datasets/{project-name}/raw/ \
  --interval 2.0 \
  --min-resolution 512 \
  --max-frames 100 \
  --start-index 25
```

| Flag | Required | Default | Description |
|---|---|---|---|
| `--video-dir` | Yes | — | Directory containing video files |
| `--output-dir` | Yes | — | Directory for extracted frames |
| `--interval` | No | 2.0 | Seconds between frame captures |
| `--min-resolution` | No | 512 | Skip frames smaller than this |
| `--max-frames` | No | 100 | Cap total extracted frames across all videos |
| `--start-index` | No | 1 | Starting number for filenames (set to continue after Step 2 downloads) |

**Outputs**:
- Sequential frame files (`025.png`, `026.png`, ...)
- `extraction-log.json` — source video, timestamp, and hash for each frame

**Behaviors**:
- Skips mostly black/white frames (transitions, fades)
- Deduplicates by file hash
- Caps total frames at `--max-frames`

### Interval Recommendations

| Video Type | Interval | Why |
|---|---|---|
| Art compilation (many different images) | 2-3s | Each image shown briefly, need frequent captures |
| Speed-paint / timelapse | 10-15s | Long stretches of similar content; or just grab the finished piece at the end |
| Game footage / cinematics | 3-5s | Moderate variety, lots of UI/HUD frames to filter |
| Artist showcase reel | 3-5s | Each piece gets a few seconds of screen time |

### Max Frames Guidance

A 30-minute video at 2s intervals produces 900 candidates. The `--max-frames` flag caps extraction to avoid flooding the dataset. For most LoRA training, 10-30 frames from video sources is plenty — video frames are supplementary to higher-quality static images.

---

## prepare_dataset.py

Resizes, crops, and organizes images into resolution buckets for training.

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/{project-name}/raw/ \
  --output-dir datasets/{project-name}/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png \
  --keep-list datasets/{project-name}/keep.txt
```

| Flag | Required | Default | Description |
|---|---|---|---|
| `--input-dir` | Yes | — | Directory with raw images |
| `--output-dir` | Yes | — | Directory for processed images |
| `--target-resolution` | No | 1024 | Target resolution: `512` or `1024` |
| `--crop-mode` | No | smart | `smart` (aspect-ratio buckets), `center`, or `square` |
| `--format` | No | png | Output format: `png` (lossless) or `jpg` |
| `--keep-list` | No | — | Text file with filenames to include (one per line). Omit to process all. |

**Outputs**:
- Sequential processed images (`001.png`, `002.png`, ...)
- `processing-report.json` — before/after resolutions, bucket counts

**Resolution buckets** (for `--crop-mode smart`):

1024px: `1024x1024`, `1152x896`, `896x1152`, `1216x832`, `832x1216`, `1344x768`, `768x1344`, `1536x640`, `640x1536`

512px: `512x512`, `576x448`, `448x576`, `640x384`, `384x640`, `768x320`, `320x768`

### Upscaling Warning

If any image needs >2x upscale, LANCZOS resampling produces noticeably blurry results. The script logs a warning for these. Options:
- **Best**: Replace with a higher-resolution version from the same source
- **Acceptable**: Use an AI upscaler (e.g., Real-ESRGAN) before running this script
- **Last resort**: Keep the LANCZOS upscale, but expect some quality loss

---

## auto_caption.py

Generates captions for training images using Florence-2, WD14 Tagger, or BLIP-2.

```bash
python scripts/auto_caption.py \
  --image-dir datasets/{project-name}/processed/ \
  --output-dir datasets/{project-name}/processed/ \
  --trigger-word "{trigger_word}" \
  --mode {style|subject|object} \
  --captioner {florence2|wd14|blip2} \
  --overwrite \
  --extra-strip-words "final fantasy,square enix"
```

| Flag | Required | Default | Description |
|---|---|---|---|
| `--image-dir` | Yes | — | Directory with images to caption |
| `--output-dir` | No | same as image-dir | Directory for `.txt` caption files |
| `--trigger-word` | Yes | — | Trigger word prepended to every caption |
| `--mode` | Yes | — | `style`, `subject`, or `object` (changes caption format) |
| `--captioner` | No | florence2 | Captioning model: `florence2`, `wd14`, or `blip2` |
| `--overwrite` | No | false | Overwrite existing caption files |
| `--extra-strip-words` | No | — | Comma-separated list of additional words to strip (project-specific style leaks) |

**Caption formats by mode**:
- `style`: `{trigger_word} style, {description of content}`
- `subject`: `{trigger_word}, {description of everything except the subject}`
- `object`: `{trigger_word}, {description of context and setting}`

**Outputs**:
- `.txt` file per image (e.g., `001.txt` alongside `001.png`)
- `caption-report.json` — captioner used, trigger word, all captions

### Caption Hygiene

The script automatically strips style-leaking and quality words from captions. This matters because auto-captioners tend to describe the art medium ("watercolor painting", "anime style"), which teaches the model to associate the trigger word with text tokens instead of learning visual features from pixels.

**Built-in blocklist includes**:
- Style terms: "watercolor", "oil painting", "anime style", "pixel art", "digital art", "cel-shaded", "3d render"
- Medium descriptors: "painting", "illustration", "photograph", "drawing", "sketch"
- Quality words: "beautiful", "masterpiece", "high quality", "stunning", "gorgeous"

Use `--extra-strip-words` for project-specific terms the blocklist misses.

---

## Captioner Comparison

| Subject Type | Recommended Captioner | Size / Requirements | Why |
|---|---|---|---|
| Realistic photos | Florence-2 | ~0.5GB download, CPU or GPU | Good natural language descriptions |
| Anime/illustration | WD14 Tagger | Separate model download | Better at anime-specific tags and character traits |
| Art styles | Florence-2 | ~0.5GB download | Describes content well; style learned by the LoRA |
| Mixed content | Florence-2 | ~0.5GB download | Most versatile, good default |
| Realistic photos (premium) | BLIP-2 | ~15GB download, 8GB+ VRAM | Higher quality than Florence-2, much larger |

**Timing expectations**: Florence-2 takes ~2-5s per image on GPU, 5-15s on CPU. For a 30-image dataset, expect 1-5 minutes. BLIP-2 is slower.

**WD14 setup**: Requires a separate model download. The script guides you through this on first run. Florence-2 also works for anime content — it produces natural language descriptions instead of tags.

---

## Required External Tools

These must be installed on the user's system. Check before starting and guide installation if missing.

| Tool | Purpose | Install |
|---|---|---|
| `yt-dlp` | Download videos from YouTube and other platforms | `pip install yt-dlp` |
| `ffmpeg` | Extract frames from downloaded videos | System package manager or https://ffmpeg.org |
| `curl` | Download images from URLs | Usually pre-installed |

### Optional (for auto-captioning)

All captioners run via `scripts/auto_caption.py`:

| Captioner | Python Packages | Install |
|---|---|---|
| Florence-2 (default) | `transformers`, `torch`, `Pillow` | `pip install transformers torch Pillow` |
| WD14 Tagger | `onnxruntime`, `Pillow`, `numpy`, `huggingface_hub` | `pip install onnxruntime Pillow numpy huggingface_hub` |
| BLIP-2 | `transformers`, `torch`, `Pillow` | `pip install transformers torch Pillow` (needs 8GB+ VRAM) |
