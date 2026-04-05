# Dataset Preparation Plan: Vintage Mechanical Keyboards

## Project Configuration

| Setting | Value | Rationale |
|---|---|---|
| Project name | `vintage-keyboards` | |
| Base model | SDXL | 1024px resolution captures keycap legend detail; widely supported |
| Target resolution | 1024 | SDXL standard |
| Trigger word | `retrokb` | Short, unique, won't collide with existing model tokens |
| Captioning mode | `object` | LoRA learns to generate vintage keyboards as objects |
| Captioner | Florence-2 | Good all-rounder for product/object photography |
| Target image count | 25-30 | Standard for object LoRA; enough variety without overfitting |

## Dataset Folder Structure

```
datasets/vintage-keyboards/
  raw/                         # Original downloaded images
  video/                       # Downloaded videos (temporary)
  processed/                   # Training-ready images + caption .txt files
  sources.json                 # Approved source list (Step 1)
  image-urls.json              # Direct image URLs (Step 2 Phase 1)
  download-log.json            # Source attribution (Step 2)
  extraction-log.json          # Video frame attribution (Step 3)
  keep.txt                     # Filenames approved in curation (Step 4)
  dataset-report.json          # Final manifest (Step 7)
```

---

## Step 1: Research Sources (COMPLETED)

See `research-report.md` and `sources.json` for full findings.

**Summary**: 15 sources identified across 3 tiers. 6 Tier A sources (Deskthority wiki pages, Reddit vintage posts, Geekhack forums), 4 Tier B sources (ClickyKeyboards, Drop, NovelKeys, Flickr), and 5 Tier C sources (3 YouTube videos, eBay, Pinterest).

**User approval needed**: Confirm which sources to pull from before proceeding to download.

---

## Step 2: Download Images

### Phase 1: Extract Image URLs

For each approved source page, use `WebFetch` to load the page and extract direct image URLs.

**Gallery pages (Deskthority, Reddit, vendors)**:
- Look for `<img>` tags with `src` attributes pointing to full-resolution images
- For Reddit: extract from `preview.redd.it` URLs, converting to `i.redd.it` for full resolution
- For Deskthority: look for wiki file links (`/wiki/File:...`) and extract the full-resolution version
- For vendor sites (Drop, NovelKeys): look for product image galleries, prefer original/zoom versions over thumbnails
- For Flickr: extract `_b.jpg` or `_o.jpg` suffixed URLs (large/original size)

**Save extracted URLs to** `datasets/vintage-keyboards/image-urls.json`:

```json
{
  "urls": [
    {"url": "https://deskthority.net/wiki/images/IBM_Model_M_top.jpg", "source_page": "https://deskthority.net/wiki/IBM_Model_M", "tier": "A"},
    {"url": "https://i.redd.it/abc123.jpg", "source_page": "https://www.reddit.com/r/MechanicalKeyboards/comments/...", "tier": "A"},
    {"url": "https://drop.com/images/gmk-retro-hero.jpg", "source_page": "https://drop.com/featured/gmk-keycaps", "tier": "B"}
  ]
}
```

### Phase 2: Download by Tier

**Tier A download** (Deskthority, Reddit, Geekhack):

```bash
python scripts/download_images.py \
  --urls-file datasets/vintage-keyboards/image-urls.json \
  --output-dir datasets/vintage-keyboards/raw/ \
  --min-resolution 512 \
  --tier A \
  --start-index 1
```

Expected result: ~20-25 images downloaded as `001.png` through `025.png` into `raw/`. Images below 512px on either dimension are skipped. Exact duplicates (by file hash) are skipped. `download-log.json` is written with source attribution for each file.

**Progress check**: Report Tier A count to user. If we have 20+ usable images from Tier A alone, Tier B may be optional.

**Tier B download** (ClickyKeyboards, vendors, Flickr):

```bash
python scripts/download_images.py \
  --urls-file datasets/vintage-keyboards/image-urls.json \
  --output-dir datasets/vintage-keyboards/raw/ \
  --min-resolution 512 \
  --tier B \
  --start-index 26
```

Expected result: ~8-12 additional images, continuing numbering from where Tier A left off. Adds professional studio photography and artistic shots for lighting diversity.

**Tier C image download** (eBay, Pinterest -- non-video sources only):

```bash
python scripts/download_images.py \
  --urls-file datasets/vintage-keyboards/image-urls.json \
  --output-dir datasets/vintage-keyboards/raw/ \
  --min-resolution 512 \
  --tier C \
  --start-index 38
```

Expected result: ~3-5 additional images. Higher rejection rate due to thumbnails, watermarks, and low resolution. Dedup catches Pinterest reposts from Reddit.

**Failure handling**:
- 403 errors from vendor sites: Skip and note; vendor CDNs often block automated downloads
- Reddit 429 rate limits: Pause, move to next source, retry later
- Thumbnail-only results: Go back to source page and look for "full size" or "original" links

---

## Step 3: Extract Video Frames

Three YouTube video sources were identified in Tier C. This step downloads them and extracts useful frames.

### Download Videos

```bash
yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/vintage-keyboards/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=example_chyrosran22_model_m_review"

yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/vintage-keyboards/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=example_chyrosran22_cherry_g80"

yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/vintage-keyboards/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=example_taekeyboards_vintage_collection"
```

Expected result: 3 video files in `datasets/vintage-keyboards/video/`, each 720p+.

### Extract Frames

These are keyboard review/showcase videos, so using a 3-5 second interval (per the scripts-reference.md recommendation for "artist showcase reel" type content where each piece gets a few seconds of screen time):

```bash
python scripts/extract_frames.py \
  --video-dir datasets/vintage-keyboards/video/ \
  --output-dir datasets/vintage-keyboards/raw/ \
  --interval 4.0 \
  --min-resolution 512 \
  --max-frames 20 \
  --start-index 43
```

The `--start-index 43` continues numbering after the ~42 images from Step 2. `--max-frames 20` caps extraction since video frames are supplementary. The 4.0s interval balances capturing different keyboard views without flooding with near-duplicate frames of the same board.

Expected result: 10-20 frames extracted as `043.png` through `062.png`. Black/white transition frames are auto-skipped. Exact duplicate hashes are skipped. `extraction-log.json` is written with source video, timestamp, and hash for each frame.

**Expected total after Steps 2-3**: ~45-55 raw images before curation.

---

## Step 4: Curate the Dataset

### Build Curation Report

Read `download-log.json` and `extraction-log.json` to compile the overview.

**Count check** (expected):

| Source | Count |
|---|---|
| Tier A downloads | ~22 |
| Tier B downloads | ~10 |
| Tier C image downloads | ~4 |
| Tier C video frames | ~15 |
| **Total raw** | **~51** |
| **Target after curation** | **25-30** |

**Quality flags to check**:
- Images below 1024px on the long edge (will need upscaling in Step 5) -- list filenames and resolutions
- eBay images with seller watermarks or text overlays -- flag for removal
- Pinterest images that are low-res reposts despite passing the 512px minimum
- Video frames showing YouTuber's face, intro/outro screens, or channel graphics rather than keyboards
- Video frames from adjacent timestamps (within 4s of each other) that show nearly identical keyboard views
- Collage images from Reddit that show multiple keyboards in a grid (should be removed or split)

**Near-duplicate detection**:
- Video frames from the same review at nearby timestamps are high risk -- flag frames within 8s of each other from the same video
- Reddit and Pinterest may contain the same image -- dedup by hash catches exact matches, but slightly different crops or resolutions need manual review
- Instruct user: "Please scan through the `raw/` folder sorted by name -- images from the same source are grouped together, which makes spotting near-duplicates easier."

**Diversity scorecard** (projected based on source mix):

| Criterion | Score | Notes |
|---|---|---|
| Subject variety | PASS | Multiple keyboard families: IBM Model M, Model F, Cherry G80, Alps, Japanese boards, modern retro builds |
| Composition range | PASS | Top-down views from wiki, profile shots from reviews, 3/4 angles from Reddit, close-ups from video frames |
| Color distribution | PASS | Beige cases are intentionally dominant (that IS the style), but keycap colors vary: grey, blue, orange, green, red modifiers |
| Background variety | WEAK | Many wiki/vendor photos use white/neutral backgrounds. Reddit desk setups add some variety. May need targeted search for keyboards in context (retro computing setups, CRT monitors) |

**Curation actions**:
- REMOVE: video frames showing non-keyboard content (faces, intros, text screens)
- REMOVE: watermarked eBay images
- REMOVE: images below 400px on either dimension (below useful even with upscaling)
- REMOVE: collage/grid images
- REMOVE: near-duplicates (keep the sharper/higher-res version)
- FLAG: images needing >2x upscale for Step 5
- KEEP: all on-target images with keyboards clearly visible

Create `keep.txt` with approved filenames after user review.

### Step 4b: Gap Analysis

**Expected bias**: Over-representation of IBM Model M (it is the most commonly photographed vintage keyboard). Need to ensure Cherry, Alps, and Japanese boards are adequately represented.

**Expected gaps**:
- Background variety is WEAK -- most images have neutral/white backgrounds. Need more "keyboards in context" shots (on retro desks, with CRT monitors, with vintage mice)
- Possible gap in close-up detail shots of keycap legends and colorful modifier keys
- May be light on Japanese vintage boards (NEC, Fujitsu) since they are rarer in Western communities

**Risk assessment**: If background variety stays WEAK, the LoRA may default to generating keyboards on white/neutral backgrounds and struggle with contextual scenes. This is acceptable for a first training run -- the LoRA mainly needs to learn the keyboard form, not backgrounds.

**Iteration decision**: With 1 WEAK criterion (background variety), this is borderline. Present to user:
- If user wants contextual generation (keyboards in scenes), iterate with targeted searches for "vintage computer setup desk" and "retro computing workspace" to find keyboards in context
- If user mainly wants isolated keyboard generation, WEAK background variety is acceptable -- proceed to Step 5

**If iterating** (targeted gap-fill):

Searches to run:
- "vintage computer desk setup IBM keyboard CRT monitor"
- "retro computing workspace 1990s"
- "mechanical keyboard desk setup vintage aesthetic"

Add new sources to `sources.json` with `"added_in": "iteration-2"`. Download into `raw/` using `--start-index` continuing from where we left off. Re-run Step 4 on the full dataset.

Cap at 2-3 iteration rounds.

---

## Step 5: Process Images

After curation approval, prepare images for training at SDXL resolution (1024px).

### Remove Rejected Images

Create `keep.txt` with one filename per line for every approved image from Step 4:

```
001.png
002.png
003.png
...
028.png
```

### Run Processing Script

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/vintage-keyboards/raw/ \
  --output-dir datasets/vintage-keyboards/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png \
  --keep-list datasets/vintage-keyboards/keep.txt
```

**What this does**:
- Reads only files listed in `keep.txt` from `raw/`
- Resizes each image to fit SDXL resolution buckets using smart aspect-ratio-aware cropping
- Available 1024px buckets: `1024x1024`, `1152x896`, `896x1152`, `1216x832`, `832x1216`, `1344x768`, `768x1344`, `1536x640`, `640x1536`
- Converts all images to lossless PNG
- Strips EXIF metadata
- Writes `processing-report.json` with before/after resolutions and bucket distribution

**Expected output**: ~28 images in `processed/` distributed across resolution buckets. Landscape keyboard photos will typically fall into `1152x896` or `1216x832`. Top-down square-ish shots into `1024x1024`. Vertical/portrait shots (rare for keyboards) into `896x1152`.

**Upscaling warning**: If any image requires >2x upscale (e.g., a 400px image being scaled to 1024px), the script warns. For those:
- Best: replace with higher-res version from the same source
- Acceptable: pre-upscale with Real-ESRGAN before running this script
- Last resort: accept LANCZOS quality loss (may appear slightly blurry in training)

---

## Step 6: Auto-Caption Images

### Configuration

- **Trigger word**: `retrokb`
- **Mode**: `object` -- captions describe context and setting, not the keyboard itself (the LoRA learns the keyboard's appearance from pixels)
- **Captioner**: Florence-2 (good all-rounder for product/object photography, ~0.5GB download, runs on CPU or GPU)
- **Extra strip words**: `"mechanical keyboard,keyboard,retro,vintage,computer keyboard"` -- these describe the object itself, which would cause style leaking since that is what the LoRA is learning

### Run Captioning

```bash
python scripts/auto_caption.py \
  --image-dir datasets/vintage-keyboards/processed/ \
  --output-dir datasets/vintage-keyboards/processed/ \
  --trigger-word "retrokb" \
  --mode object \
  --captioner florence2 \
  --overwrite \
  --extra-strip-words "mechanical keyboard,keyboard,retro,vintage,computer keyboard,typing,keys"
```

**What this does**:
- Loads Florence-2 captioning model (~0.5GB first time)
- For each image in `processed/`, generates a description
- Prepends trigger word in object mode format: `retrokb, {description of context and setting}`
- Auto-strips built-in blocklist words (quality words like "beautiful", "masterpiece"; medium words like "photograph", "illustration"; style words like "digital art")
- Also strips project-specific words from `--extra-strip-words`
- Writes one `.txt` file per image: `001.txt` alongside `001.png`
- Writes `caption-report.json` with captioner info, trigger word, and all generated captions

**Timing**: ~2-5 seconds per image on GPU, 5-15s on CPU. For 28 images, expect 1-7 minutes.

### Caption Review

After auto-captioning, review 5+ example captions (see `sample-captions.md` for expected format). Check for:
- Style-leaking words the blocklist missed (e.g., "old-fashioned", "classic", "nostalgic")
- Inaccurate descriptions (Florence-2 may misidentify keyboard parts)
- Missing important context (e.g., not mentioning the desk setup or background)
- Consistency of format across captions

If issues found, add problematic words to `--extra-strip-words` and re-run with `--overwrite`.

---

## Step 7: Generate Dataset Report

Aggregate all pipeline reports into a single manifest.

**Sources to read**:
- `processed/processing-report.json` -- image count, resolution buckets
- `processed/caption-report.json` -- captioner, trigger word, mode
- `download-log.json` -- source URLs and attribution
- `extraction-log.json` -- video frame sources
- `sources.json` -- source tiers
- Step 4 curation notes -- quality scorecard

**Output** `datasets/vintage-keyboards/dataset-report.json`:

```json
{
  "project_name": "vintage-keyboards",
  "created": "2026-04-05T12:00:00Z",
  "target_architecture": "SDXL",
  "trigger_word": "retrokb",
  "captioning_mode": "object",
  "captioning_method": "florence2",
  "caption_strip_words": ["mechanical keyboard", "keyboard", "retro", "vintage", "computer keyboard", "typing", "keys"],
  "target_resolution": 1024,
  "image_count": 28,
  "resolution_buckets": {
    "1024x1024": 6,
    "1152x896": 12,
    "896x1152": 2,
    "1216x832": 5,
    "832x1216": 1,
    "1344x768": 2
  },
  "sources_summary": {
    "tier_a": 6,
    "tier_b": 4,
    "tier_c": 5,
    "total_urls": 97,
    "images_kept": 28,
    "video_frames_used": 8,
    "iterations": 1
  },
  "quality_scorecard": {
    "subject_variety": "PASS",
    "composition_range": "PASS",
    "color_distribution": "PASS",
    "background_variety": "WEAK"
  },
  "dataset_path": "datasets/vintage-keyboards/processed/",
  "ready_for_training": true,
  "notes": "Vintage mechanical keyboard dataset focused on beige cases with colorful keycaps. 28 images covering IBM Model M/F, Cherry G80, Alps boards, and modern retro builds. Florence-2 captions in object mode. Background variety scored WEAK -- most images have neutral backgrounds. The LoRA may default to neutral backgrounds but should generalize well for keyboard form and aesthetic. 2 images required >1.5x upscale but none exceeded 2x."
}
```

---

## Step 8: Hand Off to Training

**Present to user**:

```
Dataset ready: datasets/vintage-keyboards/processed/
  - 28 images across 6 resolution buckets
  - Captioned with Florence-2 (object mode)
  - Trigger word: retrokb
  - Quality: 3 PASS, 1 WEAK (background variety)
  - Report: datasets/vintage-keyboards/dataset-report.json

To start training, say:
  "Train a LoRA using the vintage-keyboards dataset"

The training skill will read dataset-report.json to pick up your
trigger word, resolution, and captioning settings automatically.

Note: "background variety" scored WEAK -- most images have neutral
backgrounds. The LoRA may default to generating keyboards on plain
backgrounds. You can proceed with training, or gather more images
of keyboards in context (retro desk setups, CRT monitors) first.
```
