# Dataset Plan: Cyberpunk Anime Style LoRA

## Overview

| Setting | Value |
|---|---|
| Project Name | `cyberpunk-anime` |
| LoRA Type | Style |
| Base Model | SDXL |
| Target Resolution | 1024px |
| Target Image Count | 25-35 |
| Trigger Word | `cyberpunkanime` |
| Captioning Mode | `style` |
| Recommended Captioner | `wd14` (anime content) |
| Dataset Path | `datasets/cyberpunk-anime/` |

---

## Step 1: Research Sources (COMPLETE)

See `research-report.md` for full findings and `sources.json` for the structured source list.

**Summary**: 9 sources identified across 3 tiers:
- **Tier A (3 sources)**: Ghost in the Shell production art, Akira art book/Otomo illustrations, ArtStation professional cyberpunk anime art. ~32 estimated images.
- **Tier B (3 sources)**: Danbooru tagged searches, DeviantArt, Pinterest (as discovery tool). ~14 estimated images.
- **Tier C (3 sources)**: YouTube art compilations (video), Reddit communities, Wallhaven wallpapers. ~15 estimated images.

**Decision**: Present source list to user for approval. Recommend starting with all three Tier A sources, which should yield 20-25 usable images on their own.

---

## Step 2: Download Images

### Phase 1: Extract Image URLs

For each approved source, use `WebFetch` to load the page and extract direct image URLs. The process differs by source type:

**ArtStation pages (A1, A2, A3)**:
- ArtStation loads images via JavaScript; standard HTML scraping won't work
- Append `.json` to ArtStation project URLs to get API responses with direct CDN links
- Look for `image_url` fields in the JSON pointing to `cdnb.artstation.com` or `cdna.artstation.com`
- Extract full-resolution URLs (not thumbnails which end in `/small/` or `/medium/`)

**Danbooru (B1)**:
- Pages have direct links in `<img>` tags
- Look for `data-file-url` attribute on post images for full resolution
- API endpoint: `https://danbooru.donmai.us/posts.json?tags=cyberpunk+cityscape&limit=50`

**DeviantArt (B2)**:
- Use the `og:image` meta tag for each deviation page
- Gallery pages require clicking through to individual posts

**Pinterest (B3)**:
- Heavily JavaScript-dependent; WebFetch will struggle
- Better used manually as a discovery tool -- trace pins back to their original source URLs

**Wallhaven (C3)**:
- Direct image links available on individual wallpaper pages
- Look for `<img id="wallpaper"` tag for full resolution

Save the compiled URL list:

```
File: datasets/cyberpunk-anime/image-urls.json
```

```json
{
  "urls": [
    {"url": "https://cdnb.artstation.com/p/assets/.../large/image.jpg", "source_page": "https://www.artstation.com/artwork/xyz", "tier": "A"},
    {"url": "https://danbooru.donmai.us/data/original/.../image.png", "source_page": "https://danbooru.donmai.us/posts/12345", "tier": "B"}
  ]
}
```

### Phase 2: Download by Tier

**Tier A download command:**

```bash
python scripts/download_images.py \
  --urls-file datasets/cyberpunk-anime/image-urls.json \
  --output-dir datasets/cyberpunk-anime/raw/ \
  --min-resolution 512 \
  --tier A \
  --start-index 1
```

Expected result: Downloads images from all Tier A URLs, skipping anything below 512px, deduplicating by file hash. Files named `001.png`, `002.png`, etc. Produces `download-log.json` with source attribution.

**Check count after Tier A**: If we have 20+ images, we may skip Tier B. If below 20, proceed:

**Tier B download command:**

```bash
python scripts/download_images.py \
  --urls-file datasets/cyberpunk-anime/image-urls.json \
  --output-dir datasets/cyberpunk-anime/raw/ \
  --min-resolution 512 \
  --tier B \
  --start-index 22
```

(Assuming Tier A produced 21 images, `--start-index 22` continues numbering.)

**Tier C download command (if still below target):**

```bash
python scripts/download_images.py \
  --urls-file datasets/cyberpunk-anime/image-urls.json \
  --output-dir datasets/cyberpunk-anime/raw/ \
  --min-resolution 512 \
  --tier C \
  --start-index 28
```

**Failure handling**:
- 403/Forbidden from ArtStation CDN: Try alternate URL patterns or move to next source
- Low success rate on Danbooru: Use API endpoint instead of HTML scraping
- Thumbnails instead of full-res: Check for `/original/` or `/large/` in URL path components

**Output files after Step 2:**
- `datasets/cyberpunk-anime/raw/001.png` through `0XX.png`
- `datasets/cyberpunk-anime/download-log.json`

---

## Step 3: Extract Video Frames

This step applies only to source C1 (YouTube art compilations). Only proceed if static image downloads from Step 2 are below the 25-image target or lack diversity in certain composition types.

### Download Videos

```bash
yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/cyberpunk-anime/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=EXAMPLE_GITS_ART_COMPILATION"
```

```bash
yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/cyberpunk-anime/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=EXAMPLE_AKIRA_ARTBOOK_FLIPTHROUGH"
```

### Extract Frames

Art compilation videos show distinct images every few seconds, so use a 3-5s interval. Cap at 15 frames to keep video content supplementary, not dominant.

```bash
python scripts/extract_frames.py \
  --video-dir datasets/cyberpunk-anime/video/ \
  --output-dir datasets/cyberpunk-anime/raw/ \
  --interval 4.0 \
  --min-resolution 512 \
  --max-frames 15 \
  --start-index 29
```

(Assuming 28 images from Step 2; `--start-index 29` continues the sequence.)

Expected behavior:
- Extracts one frame every 4 seconds from each video
- Skips black/white transition frames automatically
- Deduplicates by hash (catches repeated title cards, etc.)
- Caps total at 15 frames across all videos
- Produces `extraction-log.json` with video source, timestamp, and hash per frame

**Output files after Step 3:**
- `datasets/cyberpunk-anime/raw/029.png` through `0XX.png` (video frames)
- `datasets/cyberpunk-anime/extraction-log.json`

---

## Step 4: Curate the Dataset

### Build the Curation Report

Read `download-log.json` and `extraction-log.json` to compile the dataset overview.

**Expected dataset at this point**: ~30-40 raw images (before curation removes some).

#### 1. Count Check

| Category | Count | Source |
|---|---|---|
| Tier A downloads | ~20 | GitS art, Akira art, ArtStation |
| Tier B downloads | ~6 | Danbooru, DeviantArt |
| Tier C downloads | ~3 | Wallhaven, Reddit |
| Video frames | ~8 | YouTube compilations |
| **Total raw** | **~37** | |
| **Target after curation** | **25-30** | |

#### 2. Quality Scan -- Flag These Issues

- **Too small**: Any image below 768px on either dimension needs flagging -- it will require >1.3x upscale for 1024px buckets. Below 512px should be removed entirely.
- **Watermarked**: DeviantArt and Pinterest-sourced images are most likely to have visible watermarks. Flag these by filename for user review.
- **Collages/multi-panel**: Some art compilation sources produce collage layouts (4+ images in a grid). These must be split into individual images or removed.
- **Off-topic**: Tier C sources may include generic anime or Western-style cyberpunk. Flag anything that doesn't match the hand-drawn, detailed anime aesthetic of GitS/Akira.
- **Text overlays**: Art book scans may include Japanese text, page numbers, or publisher logos. Flag for user review.

#### 3. Near-Duplicate Detection

- Video frames from the same compilation at timestamps within 4s of each other are likely near-duplicates (same artwork shown slightly longer)
- Images from the same ArtStation artist may include process shots (WIP versions of the same piece) -- keep only the final version
- Danbooru may have the same image uploaded at different resolutions -- keep the highest-res version

Tell user: "Please scan through the `raw/` folder sorted by name -- images from the same source are grouped together, which makes spotting near-duplicates easier."

#### 4. Diversity Scorecard

| Criterion | Expected Score | Notes |
|---|---|---|
| **Subject variety** | PASS | 5+ distinct subject types: cityscapes, characters, vehicles, interiors, mechanical details |
| **Composition range** | PASS (verify) | Need to confirm mix of wide, medium, and close-up shots |
| **Color distribution** | PASS | Both warm (Akira reds/oranges) and cool (GitS blues/teals) palettes represented |
| **Background variety** | PASS | Urban exteriors, interiors, highways, waterways, rooftops |
| **Styles** | PASS (verify) | Need 5+ different subjects rendered in the style. If too many cityscapes, need more character/action scenes |

#### 5. Recommendations to User

Present per-file recommendations:
- **Keep**: On-style, high-res, unique composition
- **Remove**: Off-topic, watermarked, too small, near-duplicate
- **"Need more like this"**: Identify which categories are underrepresented

Ask: "Please review the images in `datasets/cyberpunk-anime/raw/` and let me know if you agree with these recommendations."

---

## Step 4b: Gap Analysis and Iteration

### Bias Check

Likely biases to watch for:
- **Cityscape dominance**: Both GitS and Akira are famous for their city backgrounds, which may skew the dataset heavily toward wide exterior shots. The LoRA would then struggle with close-ups, interiors, and character scenes.
- **Night-only**: Most iconic cyberpunk anime scenes are set at night. If the dataset is all dark/night images, the LoRA may not handle daytime cyberpunk scenes well.
- **Male bias from Akira**: Akira's main cast is predominantly male. If too many character images come from Akira sources, the LoRA may associate the style with male characters.

### Gap Identification Example

Expected gaps after initial collection:
- "Close-up mechanical detail -- only 2 of 30 images" --> need 2-3 more
- "Interior environments -- only 3 images" --> borderline acceptable
- "Daytime scenes -- 0 of 30 images" --> acceptable if we want night-only aesthetic, but flag to user

### Iteration Decision

Using the diversity scorecard from Step 4:
- **Any FAIL** --> iterate (go back to Step 1 with targeted searches)
- **2+ WEAK** --> iterate
- **All PASS or 1 WEAK** --> proceed to Step 5

If iteration needed, example targeted searches:
- Gap: "not enough close-ups" --> search `"cyberpunk anime close-up detail mechanical"`, `"Ghost in the Shell cybernetics detail art"`
- Gap: "all cityscapes, no interiors" --> search `"cyberpunk anime interior lab apartment bar"`, `"Akira control room art"`

Add new sources to `sources.json` with `"added_in": "iteration-2"`. Download into same `raw/` folder with `--start-index` continuing from where previous round ended. Re-run Step 4 on the full dataset.

Cap at 2-3 iteration rounds maximum.

---

## Step 5: Process Images

After curation is complete and the user has confirmed which images to keep, process them for training.

### Create Keep List (if applicable)

If some images were flagged for removal in Step 4, create `keep.txt`:

```
datasets/cyberpunk-anime/keep.txt
```

Contents (one filename per line):
```
001.png
002.png
003.png
005.png
006.png
...
```

(Skipping `004.png` if it was flagged as a watermarked near-duplicate, for example.)

### Run Image Processing

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/cyberpunk-anime/raw/ \
  --output-dir datasets/cyberpunk-anime/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png \
  --keep-list datasets/cyberpunk-anime/keep.txt
```

**Flag breakdown:**
- `--input-dir`: Points to the raw images from Steps 2-3
- `--output-dir`: Training-ready images go here
- `--target-resolution 1024`: SDXL requires 1024px buckets
- `--crop-mode smart`: Uses aspect-ratio-aware resolution buckets (1024x1024, 1152x896, 896x1152, etc.) rather than forcing square crops
- `--format png`: Lossless output
- `--keep-list`: Only processes the approved images from curation

**Expected behavior:**
- Resizes each image to the nearest resolution bucket that matches its aspect ratio
- Converts all images to PNG format
- Strips EXIF metadata
- Renumbers files sequentially (001.png, 002.png, ...)
- Logs a warning for any image requiring >2x upscale (consider replacing those or pre-upscaling with Real-ESRGAN)

**Expected resolution bucket distribution** (for cyberpunk anime -- lots of widescreen):
- `1024x1024` (square): ~5 images
- `1152x896` (mild landscape): ~4 images
- `1344x768` (cinematic widescreen): ~8 images (many cityscapes)
- `896x1152` (mild portrait): ~3 images
- `832x1216` (tall portrait): ~2 images
- `768x1344` (very tall): ~1 image
- Other buckets: ~2 images

**Output files after Step 5:**
- `datasets/cyberpunk-anime/processed/001.png` through `0XX.png`
- `datasets/cyberpunk-anime/processed/processing-report.json`

**Upscaling warning**: If any raw images from Tier C sources (wallpapers, Reddit) are below 512px, the script will warn about >2x upscale. Recommendation: remove these and rely on higher-quality Tier A/B images, or pre-upscale with Real-ESRGAN before running prepare_dataset.py.

---

## Step 6: Auto-Caption Images

### Mode and Trigger Word

| Setting | Value | Rationale |
|---|---|---|
| **Mode** | `style` | We're training a style LoRA, not a subject or object |
| **Trigger word** | `cyberpunkanime` | Short, memorable, doesn't collide with existing tokens ("cyberpunk" and "anime" are known separately, but the compound is distinctive) |
| **Captioner** | `wd14` | WD14 Tagger is recommended for anime/illustration content. It understands anime-specific visual features better than Florence-2. |

Caption format (style mode): `cyberpunkanime style, {description of content}`

The trigger word `cyberpunkanime` would be suggested to the user for confirmation. Alternative suggestions: `cpanime`, `neotokyo_style`, `gitsakira`.

### Run Auto-Captioning

```bash
python scripts/auto_caption.py \
  --image-dir datasets/cyberpunk-anime/processed/ \
  --output-dir datasets/cyberpunk-anime/processed/ \
  --trigger-word "cyberpunkanime" \
  --mode style \
  --captioner wd14 \
  --overwrite \
  --extra-strip-words "ghost in the shell,akira,anime style,cyberpunk,neon,futuristic,sci-fi,science fiction,dystopian"
```

**Flag breakdown:**
- `--image-dir` and `--output-dir`: Same directory so .txt files sit alongside their images
- `--trigger-word "cyberpunkanime"`: Prepended to every caption in style mode format
- `--mode style`: Captions follow `{trigger_word} style, {description}` format
- `--captioner wd14`: WD14 Tagger, best for anime content
- `--overwrite`: Replace any existing caption files
- `--extra-strip-words`: Project-specific terms to strip from captions:
  - `"ghost in the shell"`, `"akira"` -- franchise names would cause the LoRA to associate the trigger with text tokens
  - `"anime style"` -- the built-in blocklist catches "anime" but we add the phrase too
  - `"cyberpunk"` -- we do NOT want the model learning trigger=cyberpunk text; it should learn the visual features
  - `"neon"`, `"futuristic"`, `"sci-fi"`, `"science fiction"`, `"dystopian"` -- these describe the style/genre, not the content. The LoRA should learn these qualities from pixels.

**Expected timing**: WD14 processes at ~2-5s per image on GPU. For 25 images, expect ~1-2 minutes total.

### Caption Hygiene

The built-in blocklist already strips:
- Style terms: "watercolor", "oil painting", "anime style", "pixel art", "digital art", "cel-shaded", "3d render"
- Medium descriptors: "painting", "illustration", "photograph", "drawing", "sketch"
- Quality words: "beautiful", "masterpiece", "high quality", "stunning", "gorgeous"

Our `--extra-strip-words` adds project-specific terms that would otherwise leak the style into captions.

**What captions SHOULD contain**: Content descriptions only -- what's in the image (city, person, motorcycle, rain, rooftop, etc.), composition (wide shot, close-up), colors (but not as style descriptors), actions, spatial relationships.

**What captions should NOT contain**: Style labels, quality judgments, franchise names, medium descriptions, genre labels.

### Review Captions

After auto-captioning, present 3-5 example captions to the user (see `sample-captions.md` for examples). Check for:
- Style-leaking words the blocklist missed (e.g., "manga", "cel animation", "retro")
- Inaccurate descriptions from WD14 auto-tagging
- Missing important details
- Consistency of format across captions

If issues found, add missing terms to `--extra-strip-words` and re-run.

**Output files after Step 6:**
- `datasets/cyberpunk-anime/processed/001.txt` through `0XX.txt` (one per image)
- `datasets/cyberpunk-anime/processed/caption-report.json`

---

## Step 7: Generate Dataset Report

Aggregate all pipeline reports into a single manifest.

**Read these files to populate the report:**
- `datasets/cyberpunk-anime/processed/processing-report.json` -- image count, resolution buckets
- `datasets/cyberpunk-anime/processed/caption-report.json` -- captioner, trigger word, mode
- `datasets/cyberpunk-anime/download-log.json` -- source URLs and attribution
- `datasets/cyberpunk-anime/extraction-log.json` -- video frame sources (if Step 3 was used)
- `datasets/cyberpunk-anime/sources.json` -- source tiers
- Step 4 curation notes -- quality scorecard

**Expected dataset-report.json:**

```json
{
  "project_name": "cyberpunk-anime",
  "created": "2026-04-05T14:00:00Z",
  "target_architecture": "SDXL",
  "trigger_word": "cyberpunkanime",
  "captioning_mode": "style",
  "captioning_method": "wd14",
  "caption_strip_words": [
    "ghost in the shell", "akira", "anime style", "cyberpunk",
    "neon", "futuristic", "sci-fi", "science fiction", "dystopian"
  ],
  "target_resolution": 1024,
  "image_count": 27,
  "resolution_buckets": {
    "1024x1024": 5,
    "1152x896": 4,
    "1344x768": 8,
    "896x1152": 3,
    "832x1216": 2,
    "1216x832": 3,
    "768x1344": 1,
    "1536x640": 1
  },
  "sources_summary": {
    "tier_a": 3,
    "tier_b": 3,
    "tier_c": 3,
    "total_urls": 55,
    "images_downloaded": 37,
    "images_kept": 27,
    "video_frames_used": 6,
    "iterations": 1
  },
  "quality_scorecard": {
    "subject_variety": "PASS",
    "composition_range": "PASS",
    "color_distribution": "PASS",
    "background_variety": "PASS",
    "styles": "PASS"
  },
  "dataset_path": "datasets/cyberpunk-anime/processed/",
  "ready_for_training": true,
  "notes": "Cyberpunk anime style LoRA dataset inspired by Ghost in the Shell and Akira. 27 images with WD14 captions. Mix of cityscapes (8), character scenes (6), vehicles/machinery (4), close-up details (4), interiors (3), action scenes (2). Mostly widescreen compositions reflecting the cinematic framing typical of the genre. 6 images sourced from video frame extraction. No images required >2x upscale."
}
```

Save to `datasets/cyberpunk-anime/dataset-report.json`.

---

## Step 8: Hand Off to Training

Present the following summary to the user:

```
Dataset ready: datasets/cyberpunk-anime/processed/
  - 27 images across 8 resolution buckets
  - Captioned with WD14 Tagger (style mode)
  - Trigger word: cyberpunkanime
  - Quality: all scorecard criteria PASS
  - Report: datasets/cyberpunk-anime/dataset-report.json

To start training, say:
  "Train a LoRA using the cyberpunk-anime dataset"

The training skill will read dataset-report.json to pick up your
trigger word, resolution, and captioning settings automatically.
```

---

## Complete Folder Structure After Pipeline

```
datasets/cyberpunk-anime/
  raw/                              # 37 original downloaded images
    001.png ... 037.png
  video/                            # Downloaded videos (can delete after extraction)
    ghost-in-the-shell-art.mp4
    akira-artbook-flipthrough.mp4
  processed/                        # 27 training-ready images + captions
    001.png
    001.txt
    002.png
    002.txt
    ...
    027.png
    027.txt
    processing-report.json
    caption-report.json
  sources.json
  image-urls.json
  download-log.json
  extraction-log.json
  keep.txt
  dataset-report.json
```

---

## Script Command Summary (Quick Reference)

| Step | Command |
|---|---|
| Download Tier A | `python scripts/download_images.py --urls-file datasets/cyberpunk-anime/image-urls.json --output-dir datasets/cyberpunk-anime/raw/ --min-resolution 512 --tier A --start-index 1` |
| Download Tier B | `python scripts/download_images.py --urls-file datasets/cyberpunk-anime/image-urls.json --output-dir datasets/cyberpunk-anime/raw/ --min-resolution 512 --tier B --start-index 22` |
| Download Tier C | `python scripts/download_images.py --urls-file datasets/cyberpunk-anime/image-urls.json --output-dir datasets/cyberpunk-anime/raw/ --min-resolution 512 --tier C --start-index 28` |
| Video download | `yt-dlp -f "bestvideo[height>=720]" -o "datasets/cyberpunk-anime/video/%(title)s.%(ext)s" "{url}"` |
| Frame extraction | `python scripts/extract_frames.py --video-dir datasets/cyberpunk-anime/video/ --output-dir datasets/cyberpunk-anime/raw/ --interval 4.0 --min-resolution 512 --max-frames 15 --start-index 29` |
| Process images | `python scripts/prepare_dataset.py --input-dir datasets/cyberpunk-anime/raw/ --output-dir datasets/cyberpunk-anime/processed/ --target-resolution 1024 --crop-mode smart --format png --keep-list datasets/cyberpunk-anime/keep.txt` |
| Auto-caption | `python scripts/auto_caption.py --image-dir datasets/cyberpunk-anime/processed/ --output-dir datasets/cyberpunk-anime/processed/ --trigger-word "cyberpunkanime" --mode style --captioner wd14 --overwrite --extra-strip-words "ghost in the shell,akira,anime style,cyberpunk,neon,futuristic,sci-fi,science fiction,dystopian"` |
