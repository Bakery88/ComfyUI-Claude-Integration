# Dataset Preparation Plan: Yoshitaka Amano JRPG Watercolor Style

## Project Configuration

| Parameter | Value | Rationale |
|---|---|---|
| Project name | `jrpg-amano-style` | Descriptive, filesystem-safe |
| Base model | FLUX | Best current quality for stylistic LoRAs |
| Target resolution | 1024 | FLUX native resolution |
| Trigger word | `amanoart` | Short, unique, memorable, no token collision |
| Captioning mode | `style` | Learning an art style, not a specific subject |
| Captioner | `florence2` | Best for art styles; describes content well |
| Target image count | 25-30 | Standard for style LoRAs |

## Folder Structure

```
datasets/jrpg-amano-style/
  raw/                         # Original downloaded images
  video/                       # Downloaded videos (temporary)
  processed/                   # Training-ready images + caption .txt files
  sources.json                 # Approved source list (Step 1)
  image-urls.json              # Direct image URLs (Step 2 Phase 1)
  download-log.json            # Source attribution (Step 2)
  extraction-log.json          # Video frame attribution (Step 3)
  keep.txt                     # Filenames to keep after curation (Step 4)
  dataset-report.json          # Final manifest (Step 7)
```

---

## Step 1: Research Sources -- COMPLETE

See `research-report.md` and `sources.json` for full details.

**Summary**: 9 sources identified across 3 tiers. Tier A (4 sources) provides 95-120 estimated usable images -- more than enough. Tier B (3 sources) provides gap-filling variety. Tier C (2 video sources) provides opportunistic frame grabs.

**User approval needed**: Present the source list and get confirmation before downloading.

---

## Step 2: Download Images

### Phase 1: Extract Image URLs

For each approved source, use `WebFetch` to load the page and extract direct image URLs.

**For the FF Wiki gallery (src-01)**:
- Fetch `https://finalfantasy.fandom.com/wiki/Yoshitaka_Amano/Gallery`
- Extract all `<img>` tags, looking for full-resolution links (not thumbnails)
- Wiki images typically have `/revision/latest` URLs -- use those for full resolution
- Filter to `.png` and `.jpg` files only

**For Amano's official site (src-02)**:
- Fetch `https://www.amanoyoshitaka.com`
- Site may use JavaScript rendering -- check for API endpoints or JSON data in page source
- Look for portfolio/gallery subpages and crawl each

**For art book scans (src-03)**:
- Fetch the wiki page for image references, then follow links to full-size scans
- Also search community forums for high-res uploads

**For Danbooru (src-06)**:
- Fetch `https://danbooru.donmai.us/posts?tags=amano_yoshitaka+official_art+score%3A%3E5`
- Extract `file_url` from each post's metadata (Danbooru has a JSON API: append `.json` to post URLs)

Save the consolidated URL list:

```
datasets/jrpg-amano-style/image-urls.json
```

Format:
```json
{
  "urls": [
    {"url": "https://static.wikia.nocookie.net/..../001.png", "source_page": "https://finalfantasy.fandom.com/...", "tier": "A"},
    {"url": "https://cdn.donmai.us/original/..../hash.jpg", "source_page": "https://danbooru.donmai.us/posts/12345", "tier": "B"}
  ]
}
```

### Phase 2: Download by Tier

**Tier A download:**

```bash
python scripts/download_images.py \
  --urls-file datasets/jrpg-amano-style/image-urls.json \
  --output-dir datasets/jrpg-amano-style/raw/ \
  --min-resolution 512 \
  --tier A \
  --start-index 1
```

**Expected result**: 25-40 images downloaded as `001.png`, `002.png`, etc. into `raw/`. Images below 512px on either dimension are skipped. Exact duplicates (by hash) are skipped. A `download-log.json` is written with source attribution for each file.

**Progress check**: Report count to user after Tier A completes.
- If 25+ images: Tier A alone is sufficient. Skip Tier B unless diversity gaps found in Step 4.
- If 15-24 images: Proceed with Tier B.
- If <15 images: Proceed with Tier B and C.

**Tier B download (if needed):**

```bash
python scripts/download_images.py \
  --urls-file datasets/jrpg-amano-style/image-urls.json \
  --output-dir datasets/jrpg-amano-style/raw/ \
  --min-resolution 512 \
  --tier B \
  --start-index 41
```

(Where `--start-index 41` continues numbering from wherever Tier A left off -- e.g., if Tier A produced 40 images, start at 41.)

**Tier C download (if needed):**

```bash
python scripts/download_images.py \
  --urls-file datasets/jrpg-amano-style/image-urls.json \
  --output-dir datasets/jrpg-amano-style/raw/ \
  --min-resolution 512 \
  --tier C \
  --start-index 51
```

### Handling Download Failures

- **403/Forbidden**: Move to next source. Don't fight uncooperative sites.
- **Low success rate (<30%)**: Source likely uses JS-rendered images. Flag and try next source.
- **Thumbnails only**: Go back to source page and look for "full size" / "original" links.
- **Rate limiting (429s)**: Pause source, move to next, come back later.

---

## Step 3: Extract Video Frames

Applies only to src-08 and src-09 (YouTube video sources, Tier C). Only proceed if image count from Step 2 is below target.

### Download Videos

```bash
yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/jrpg-amano-style/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=EXAMPLE_SHOWCASE_VIDEO_ID"
```

```bash
yt-dlp -f "bestvideo[height>=720]" \
  -o "datasets/jrpg-amano-style/video/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=EXAMPLE_PROCESS_VIDEO_ID"
```

### Extract Frames

For the art showcase compilation (src-08) -- use 3-5s interval since each artwork is shown briefly:

```bash
python scripts/extract_frames.py \
  --video-dir datasets/jrpg-amano-style/video/ \
  --output-dir datasets/jrpg-amano-style/raw/ \
  --interval 4.0 \
  --min-resolution 512 \
  --max-frames 15 \
  --start-index 51
```

(Where `--start-index 51` continues numbering after Step 2 downloads.)

**Expected result**: 10-15 frames extracted as `051.png`, `052.png`, etc. Black/white transition frames skipped automatically. Hash dedup catches near-identical frames. Capped at 15 frames total.

For painting process/timelapse videos (src-09) -- use longer interval since content changes slowly:

```bash
python scripts/extract_frames.py \
  --video-dir datasets/jrpg-amano-style/video/ \
  --output-dir datasets/jrpg-amano-style/raw/ \
  --interval 15.0 \
  --min-resolution 512 \
  --max-frames 5 \
  --start-index 66
```

**Expected result**: 2-5 frames, primarily the finished painting at the end of each timelapse.

---

## Step 4: Curate the Dataset

### Curation Report

After downloading, read `download-log.json` and `extraction-log.json` to compile:

**1. Count Check (example)**:
- Total images gathered: 38
- From Tier A downloads: 28
- From Tier B downloads: 5
- From video frames: 5
- Target: 25-30
- Status: Above target -- good, we can be selective during curation

**2. Quality Scan -- Flag These Issues**:

| Issue | What to Look For | Action |
|---|---|---|
| Too small | Images below 512px on either dimension | Remove (should be caught by `--min-resolution` but verify) |
| Watermarks | Art book scans with publisher watermarks, gallery site watermarks | Flag to user; likely remove |
| Text overlays | Title cards, logos, "Square Enix" text on promotional art | Remove or crop if the art is otherwise good |
| Collages | Multi-character spreads or art book double-pages | Split into individual pieces or remove |
| Off-topic | Fan art that slipped through, sprite art, game screenshots | Remove |
| Muddy scans | Dark, low-contrast scans that don't represent the luminous watercolor quality | Remove |
| Near-duplicates | Same artwork at different crops/resolutions from different sources | Keep the highest-quality version only |

**3. Near-Duplicate Detection**:
- Review video frames from the same source at nearby timestamps (frames within 2-4s are likely near-duplicates)
- Check images from the same source with similar filenames or sequential numbering
- Tell user: "Please scan through the `raw/` folder sorted by name -- images from the same source are grouped together, making near-duplicates easier to spot."

**4. Diversity Scorecard**:

| Criterion | Expected Score | Notes |
|---|---|---|
| Subject variety | PASS | FF has many distinct characters; include Vampire Hunter D for non-FF subjects |
| Composition range | PASS/WEAK | Amano tends toward full-body character portraits; may need to seek close-ups |
| Color distribution | PASS | Amano's palette is varied -- blues, golds, purples, greens across different pieces |
| Background variety | WEAK | Many Amano pieces have abstract/minimal backgrounds; this IS the style, so acceptable |
| Styles (subject diversity) | PASS | 5+ distinct characters/subjects in the Amano style is achievable |

**5. Curation Decision**:
- Present per-file recommendations (keep/remove/need-more-like-this)
- Show the diversity scorecard
- Ask user to review `datasets/jrpg-amano-style/raw/` and confirm

### Step 4b: Gap Analysis

**Likely Bias**: Most Amano artwork features standing/posed characters in full-body view. The dataset may be weak on:
- Close-up portrait compositions
- Action/dynamic poses
- Landscape-only pieces (no characters)
- Dark/moody color palettes (most Amano is luminous)

**Risk Assessment**: The LoRA may struggle to apply the Amano style to close-up portraits or landscape compositions if the training data is all full-body character art.

**Iteration Decision**:
- If diversity scorecard shows any FAIL or 2+ WEAK: iterate with targeted searches
- Example targeted searches for gap-filling:
  - "Yoshitaka Amano close-up portrait detail" (for composition variety)
  - "Yoshitaka Amano landscape background environment" (for non-character pieces)
  - "Yoshitaka Amano dark moody illustration" (for color range)
- Add new sources to `sources.json` with `"added_in": "iteration-2"`
- Download with `--start-index` continuing from previous count
- Re-run Step 4 on the full combined dataset

**Iteration cap**: 2-3 rounds maximum. After that, train with what we have.

### Creating keep.txt

After curation, write a `keep.txt` with one filename per line for images that passed review:

```
001.png
002.png
003.png
005.png
007.png
...
```

(Note: files 004 and 006 removed due to quality issues, for example.)

Save to `datasets/jrpg-amano-style/keep.txt`.

---

## Step 5: Process Images

### Remove Rejected Images and Prepare for Training

Run `prepare_dataset.py` with FLUX-appropriate settings:

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/jrpg-amano-style/raw/ \
  --output-dir datasets/jrpg-amano-style/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png \
  --keep-list datasets/jrpg-amano-style/keep.txt
```

**What this does**:
1. Reads only files listed in `keep.txt` from `raw/`
2. Resizes each image to fit into the nearest FLUX resolution bucket:
   - `1024x1024`, `1152x896`, `896x1152`, `1216x832`, `832x1216`, `1344x768`, `768x1344`, `1536x640`, `640x1536`
3. Uses smart cropping to preserve the most important part of each image
4. Converts all images to PNG (lossless)
5. Strips EXIF metadata
6. Renames files sequentially: `001.png`, `002.png`, ...
7. Writes `processed/processing-report.json` with before/after resolutions and bucket distribution

**Expected output**: 25-30 processed PNG images in resolution buckets, plus the processing report.

**Upscaling warning**: If any image needs >2x upscale (e.g., a 400px image being scaled to 1024px), the script logs a warning. For those images:
- Best: replace with a higher-resolution version from the same source
- Acceptable: pre-upscale with Real-ESRGAN before running this script
- Last resort: keep the LANCZOS upscale but note quality loss

**Expected resolution bucket distribution** (for Amano art, which tends toward portrait orientation):

| Bucket | Expected Count | Why |
|---|---|---|
| `896x1152` | 8-10 | Most Amano character art is portrait-oriented |
| `1024x1024` | 5-7 | Square-ish promotional art and key visuals |
| `1152x896` | 4-6 | Landscape-oriented scenes and group compositions |
| `832x1216` | 2-4 | Tall, narrow character portraits |
| `1216x832` | 1-3 | Wide panoramic pieces |

---

## Step 6: Auto-Caption Images

### Trigger Word

- **Proposed**: `amanoart`
- **Rationale**: Short (1 word), unique (not a common English word or known model token), clearly evocative of the subject
- **User confirmation needed** before proceeding

### Captioning Mode

- **Mode**: `style`
- **Format**: `amanoart style, {description of content}`
- **Rationale**: We want the LoRA to learn the visual rendering technique, not specific characters. The caption describes WHAT is in the image; the LoRA learns HOW it was rendered from the pixels.

### Run Auto-Captioning

```bash
python scripts/auto_caption.py \
  --image-dir datasets/jrpg-amano-style/processed/ \
  --output-dir datasets/jrpg-amano-style/processed/ \
  --trigger-word "amanoart" \
  --mode style \
  --captioner florence2 \
  --overwrite \
  --extra-strip-words "final fantasy,square enix,yoshitaka amano,amano,watercolor,painting,illustration,jrpg,rpg,video game,concept art"
```

**Flag breakdown**:
- `--image-dir` / `--output-dir`: Both point to `processed/` so `.txt` files sit alongside their `.png` files
- `--trigger-word "amanoart"`: Prepended to every caption as `amanoart style, ...`
- `--mode style`: Uses the style caption format
- `--captioner florence2`: Best choice for art styles -- describes content well without over-focusing on medium
- `--overwrite`: Replaces any existing caption files (useful if re-running after adjustments)
- `--extra-strip-words`: Project-specific terms to strip from captions. This is critical:
  - `"final fantasy"`, `"square enix"` -- franchise names that would leak into the trigger association
  - `"yoshitaka amano"`, `"amano"` -- artist name must not appear (the LoRA learns the style from pixels, not text)
  - `"watercolor"`, `"painting"`, `"illustration"` -- medium descriptors (already in built-in blocklist, but reinforced here)
  - `"jrpg"`, `"rpg"`, `"video game"`, `"concept art"` -- genre terms that would narrow the LoRA's applicability

**What the built-in blocklist already strips**:
- Style terms: "watercolor", "oil painting", "anime style", "pixel art", "digital art", "cel-shaded", "3d render"
- Medium descriptors: "painting", "illustration", "photograph", "drawing", "sketch"
- Quality words: "beautiful", "masterpiece", "high quality", "stunning", "gorgeous"

**Expected timing**: Florence-2 at ~2-5s per image on GPU, 5-15s on CPU. For 25-30 images: 1-5 minutes total.

**Output**: One `.txt` file per image (e.g., `001.txt` alongside `001.png`), plus `caption-report.json`.

### Caption Review

After auto-captioning, review 3-5 example captions (see `sample-captions.md`) to check for:
- Style-leaking words the blocklist missed
- Inaccurate descriptions
- Missing important details
- Consistency of format

If issues found: add missed words to `--extra-strip-words` and re-run with `--overwrite`.

---

## Step 7: Generate Dataset Report

Read the pipeline's existing reports and aggregate into `dataset-report.json`:

```json
{
  "project_name": "jrpg-amano-style",
  "created": "2026-04-05T12:00:00Z",
  "target_architecture": "FLUX",
  "trigger_word": "amanoart",
  "captioning_mode": "style",
  "captioning_method": "florence2",
  "caption_strip_words": [
    "final fantasy", "square enix", "yoshitaka amano", "amano",
    "watercolor", "painting", "illustration", "jrpg", "rpg",
    "video game", "concept art"
  ],
  "target_resolution": 1024,
  "image_count": 27,
  "resolution_buckets": {
    "896x1152": 9,
    "1024x1024": 6,
    "1152x896": 5,
    "832x1216": 4,
    "1216x832": 3
  },
  "sources_summary": {
    "tier_a": 4,
    "tier_b": 3,
    "tier_c": 2,
    "total_urls": 55,
    "images_kept": 27,
    "video_frames_used": 4,
    "iterations": 1
  },
  "quality_scorecard": {
    "subject_variety": "PASS",
    "composition_range": "PASS",
    "color_distribution": "PASS",
    "background_variety": "WEAK",
    "styles_subject_diversity": "PASS"
  },
  "dataset_path": "datasets/jrpg-amano-style/processed/",
  "ready_for_training": true,
  "notes": "Focus on Amano's classic FF I-VI era watercolor style. 27 images including 4 Vampire Hunter D pieces for subject diversity. Florence-2 captions with aggressive style-leak stripping. Background variety scored WEAK -- Amano's abstract backgrounds are an intentional style feature, not a dataset gap."
}
```

Save to `datasets/jrpg-amano-style/dataset-report.json`.

---

## Step 8: Hand Off to Training

Present this summary to the user:

```
Dataset ready: datasets/jrpg-amano-style/processed/
  - 27 images across 5 resolution buckets
  - Captioned with Florence-2 (style mode)
  - Trigger word: amanoart
  - Quality: 4/5 scorecard criteria PASS, 1 WEAK
  - Report: datasets/jrpg-amano-style/dataset-report.json

Note: "background_variety" scored WEAK -- most images have abstract/minimal
backgrounds, which is characteristic of Amano's actual style. This is
expected and should not cause issues. If you want the LoRA to also
handle detailed environments, consider gathering more landscape pieces.

To start training, say:
  "Train a LoRA using the jrpg-amano-style dataset"

The training skill will read dataset-report.json to pick up your
trigger word, resolution, and captioning settings automatically.
```
