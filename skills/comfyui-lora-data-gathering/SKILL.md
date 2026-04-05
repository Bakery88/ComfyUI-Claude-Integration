---
name: comfyui-lora-data-gathering
description: >
  Use this skill when the user wants to gather, collect, or prepare training images for LoRA fine-tuning.
  Covers the full pipeline: web research, image downloading, video frame extraction, dataset curation,
  image processing, and auto-captioning. Use it when the user mentions collecting images from the web,
  building a training dataset, finding reference images for a style or subject, or preparing images
  they already have into a LoRA-ready dataset. Also use it when they say things like "I want to train
  a LoRA but I don't have images yet" or "help me find training data." Do NOT use this skill if the
  user already has a prepared dataset and just wants to start training — that's comfyui-lora-training.
---

# Skill: ComfyUI LoRA Data Gathering

> Research, collect, and prepare training datasets for LoRA fine-tuning. Handles the full pipeline from web research through image download, video frame extraction, and auto-captioning — delivering a ready-to-train dataset folder.

## When to Use

- User asks "Help me gather LoRA data for [subject/style]" or "Find training images for..."
- User wants to build a dataset for LoRA training but doesn't have images yet
- User has a concept (art style, character type, aesthetic) and needs reference material collected
- User mentions collecting images from the web, YouTube, or art communities for training
- User says something like "I want to train a LoRA on [style] but I don't have any images"
- User asks to prepare or organize images they've found into a training dataset

If the user already has their images and just needs training guidance, redirect to `comfyui-lora-training` instead.

## Dependencies

- **comfyui-inventory**: Check available base models to recommend appropriate dataset resolution (FLUX = 1024px, SDXL = 1024px, SD 1.5 = 512px)
- **comfyui-lora-training**: This skill's output feeds directly into lora-training's Step 2 (Dataset Preparation). All gathered data must meet those requirements.
- **Outputs**: `datasets/{project-name}/` folder with images, captions, and a `dataset-report.json` manifest

## Tools Used

| Tool | Purpose |
|---|---|
| `WebSearch` | Find image sources, art communities, video tutorials, reference sheets |
| `WebFetch` | Crawl pages to extract image URLs and metadata |
| `list_models` | Check base model to determine target resolution |
| Scripts in `scripts/` | Download images, extract video frames, process images, generate captions |

**External tools required**: `yt-dlp`, `ffmpeg`, `curl`, plus Python packages for auto-captioning.

**Before running any script**: Read `references/scripts-reference.md` for exact CLI flags, usage examples, and install commands. Each script step below will remind you, but don't skip it — the reference doc has details not repeated here (resolution bucket tables, captioner comparison, interval recommendations).

## Clarification Interview

This skill deals with subjective, creative goals — the more context gathered upfront, the better the dataset. When a request is vague or exploratory, ask clarifying questions before researching. The goal is to understand what visual qualities the user wants the LoRA to learn.

### Questions to Ask

Don't dump all of these at once. Pick the most relevant 2-3 based on what the user said, and infer what you can from context.

**Always ask (if not already clear)**:
1. **What should the LoRA learn?** A specific person's face, an art style, a type of object, an aesthetic/mood?
2. **What base model will you train on?** FLUX, SDXL, or SD 1.5? (This determines target resolution and captioning approach.)

**Ask when relevant**:
3. **Can you name specific examples?** Artists, games, shows, products — concrete references help narrow the search enormously.
4. **What visual qualities matter most?** Color palette, line weight, composition, texture, lighting style?
5. **What should it NOT look like?** Knowing the boundaries of the style helps filter out near-misses.
6. **How many images are you aiming for?** Default is 20-30, but some subjects need more variety.

### When to Skip the Interview

If the user's request is already specific enough to act on (e.g., "Gather 20 images of Yoshitaka Amano's JRPG artwork from Final Fantasy"), go straight to research. You can always ask follow-up questions as you discover things.

## Procedure

### Step 1: Research Sources

Use `WebSearch` to find high-quality sources for the target subject/style. Search strategically based on what the user is training:

**For art styles**:
- Search for the artist name, art movement, or game/show title
- Look for art galleries, fan wikis, portfolio sites, artstation/deviantart collections
- Search YouTube for speed-paints, art tutorials, or "art of [franchise]" compilations
- Look for official art books or reference sheets

**For people/characters**:
- Search for high-res photo sets with varied angles, lighting, expressions
- Look for press photos, portfolio shoots, convention photos
- Avoid heavily filtered/edited images — they confuse the LoRA

**For objects/products**:
- Search for product photography, catalog images, 360-degree views
- Look for different angles, scales, and contexts

**For aesthetics/moods**:
- Search for mood boards, Pinterest collections, photography styles
- Look for the aesthetic name + "photography" or "art" or "design"

**Tier your sources** as you go. Not all sources are equal — prioritize by likely quality and relevance:

- **Tier A (Primary)**: Official artwork, artist portfolios, high-res galleries, art books. These are your backbone — consistent quality, on-style.
- **Tier B (Supplementary)**: Community archives (Danbooru, DeviantArt), fan wikis, curated Pinterest boards. Good for variety but need more filtering.
- **Tier C (Opportunistic)**: General search results, video frame grabs, social media. Use these to fill gaps, but expect a lower hit rate.

Build a source list as you go:

```json
{
  "sources": [
    {
      "url": "https://...",
      "type": "gallery|video|article|reference-sheet",
      "tier": "A|B|C",
      "description": "What this source contains",
      "estimated_usable_images": 10
    }
  ]
}
```

Present the source list to the user for approval before downloading. The user should confirm which sources to pull from, since they know best what matches their vision — and some sources may have licensing they care about. Aim for at least 2-3 Tier A sources before relying on lower tiers.

### Step 2: Download Images

This step turns the approved source list into actual image files. It has two phases: extracting direct image URLs from source pages, then downloading them.

#### Phase 1: Extract Image URLs

Most sources from Step 1 are page URLs (galleries, portfolios), not direct image links. For each approved source, use `WebFetch` to load the page and extract direct image URLs:

- Look for `<img>` tags, OpenGraph images, and links to `.png`/`.jpg`/`.webp` files
- For gallery pages, look for "full size" or "original" links — thumbnails are too small for training
- For sites that load images via JavaScript (ArtStation, some portfolio sites), the initial HTML may not contain image URLs. Try appending `.json` to ArtStation URLs or look for API endpoints in the page source

Build a flat URL list grouped by tier and save it:

```json
{
  "urls": [
    {"url": "https://direct-image-link.jpg", "source_page": "https://gallery-page", "tier": "A"},
    {"url": "https://another-image.png", "source_page": "https://portfolio-page", "tier": "B"}
  ]
}
```

Save this as `datasets/{project-name}/image-urls.json`.

#### Phase 2: Download by Tier

Download in tier order — Tier A first, then B, then C — checking progress between each tier. Use `scripts/download_images.py` with `--tier A`, then `--tier B` with `--start-index` to continue numbering.

**Important**: Set `--start-index` to the actual file count from the previous tier, not an estimate. Check how many files are in `raw/` before each tier download. Read `references/scripts-reference.md` before running — it has the full flag reference and usage examples.

After Tier A completes, report the count to the user:
- If already at or near the target count (20-30), lower tiers may not be needed
- If below target, proceed with Tier B then C

The script handles downloading, minimum resolution filtering, dedup by file hash, sequential naming, and writing `download-log.json` with source attribution.

#### When Downloads Fail

Some common issues and how to handle them:
- **403/Forbidden**: The site blocks automated downloads. Move to a different source rather than fighting it.
- **Low success rate** (<30% of URLs work): The source page likely uses lazy loading or JS-rendered images that `WebFetch` couldn't extract. Flag to the user and try the next source.
- **Images are thumbnails**: Go back to the source page and look for full-resolution links. Many galleries serve thumbnails by default.
- **Rate limiting (429s)**: Pause this source and move to the next. Come back later if needed.

Don't spend excessive time on uncooperative sources — there are usually easier alternatives.

### Step 3: Extract Video Frames

**When to use this step**: Only when the approved source list from Step 1 includes video sources (type `"video"`). If all sources are image galleries or pages, skip to Step 4.

Video sources are useful for art compilations, speed-paint timelapses, game footage, and "art of" showcase reels. The goal is to extract the distinct, high-quality frames — not every frame of the video.

#### Download Videos

Download each approved video source using yt-dlp:

```bash
yt-dlp -f "bestvideo[height>=720]" -o "datasets/{project-name}/video/%(title)s.%(ext)s" "{video_url}"
```

Only download videos from approved sources. Respect the tier system — prioritize Tier A video sources (official art reels, artist channels) over Tier C (random compilations).

#### Extract Frames

Use `scripts/extract_frames.py`, setting `--start-index` to the actual number of files currently in `raw/` (not an estimate — count them). Read `references/scripts-reference.md` before running — it has interval recommendations by video type, max-frames guidance, and all CLI flags.

The script extracts frames at regular intervals, skips low-resolution and black/white frames (transitions), deduplicates by hash, and caps total frames via `--max-frames`. For most LoRA training, 10-30 frames from video sources is plenty — they supplement the higher-quality static images from Step 2.

### Step 4: Curate the Dataset

This is a collaborative step. You can't display images directly — so your job is to build a clear picture of the dataset from the metadata, flag issues, and guide the user through reviewing the actual files in their file browser.

#### Build the Curation Report

Read `download-log.json` (from Step 2) and `extraction-log.json` (from Step 3, if applicable) to compile a dataset overview:

1. **Count check**: Report total images gathered vs. the target (20-30 typical). Break down by source tier and source type (downloaded vs. video frames).

2. **Quality scan**: Flag specific files that might cause training issues. Reference filenames so the user can find them:
   - Too small (below target resolution) — list filenames and their resolutions
   - Suspected watermarks or text overlays — flag images from sources known for watermarking
   - Collages or multi-panel images (should be split or removed)
   - Off-topic images — flag any from Tier C sources or sources with low relevance

3. **Near-duplicate detection**: Images that are very similar but not byte-identical (e.g., slightly different crops, video frames from adjacent timestamps) waste training budget. To catch these:
   - Review video frames from the same source at nearby timestamps — consecutive frames within 2-4s of each other are likely near-duplicates
   - Flag images from the same source page that have similar filenames or sequential numbering
   - Tell the user: "Please scan through the `raw/` folder sorted by name — images from the same source are grouped together, which makes spotting near-duplicates easier."

4. **Diversity checklist**: Score each criterion as PASS / WEAK / FAIL:

   | Criterion | PASS | WEAK | FAIL |
   |---|---|---|---|
   | **Subject variety** | 5+ distinct subjects/scenes | 3-4 subjects | <3 (dataset will overfit to specific subjects) |
   | **Composition range** | Has close-ups, medium, and wide shots | Missing one type | All same framing |
   | **Color distribution** | Varied palette (or single palette IS the style) | Slightly skewed | Dominated by one palette unintentionally |
   | **Background variety** | 3+ different settings/contexts | 2 settings | All same background |
   | **People** (if applicable) | 3+ expressions, 3+ lighting setups, varied clothing | Partial variety | All same pose/expression/lighting |
   | **Styles** (if applicable) | 5+ different subjects in the style | 3-4 subjects | <3 (will learn subject, not style) |

5. **Present the summary** to the user with:
   - Per-file recommendations: keep, remove, or "need more like this"
   - The diversity scorecard above
   - A clear ask: "Please review the images in `datasets/{project-name}/raw/` and let me know if you agree with these recommendations, or if you'd like to adjust."

### Step 4b: Gap Analysis and Iteration

After curation, step back and assess the dataset as a whole. This is where you catch problems that per-image review misses.

#### Analysis

- **Bias check**: Is the dataset skewed? (e.g., all female characters, all daytime scenes, all the same angle). A biased dataset trains a biased LoRA — the model will struggle to generalize beyond what it's seen.
- **Gap identification**: List specific gaps with concrete counts ("no close-up portraits — 0 of 25 images", "missing dark/moody lighting — only 1 image", "only 2 images with backgrounds, rest are isolated subjects").
- **Risk assessment**: What will the LoRA likely struggle with given this dataset? Be specific ("may not generalize to non-human subjects since all 20 training images are portraits of people").

#### When to Iterate

Use the diversity scorecard from Step 4 to decide:

- **Any FAIL criterion** → iterate. A FAIL means the LoRA will have a blind spot that's hard to fix after training.
- **2+ WEAK criteria** → iterate. One WEAK is acceptable, but multiple compound into a mediocre dataset.
- **All PASS or 1 WEAK** → proceed to Step 5. The dataset is solid enough.

Always present the analysis to the user and let them override — they may know that a "gap" is intentional (e.g., "I only want daytime scenes").

#### How to Iterate

When looping back, don't redo the broad search from Step 1. Instead:

1. **Write targeted search queries** that specifically address the gaps. For example, if the dataset is all wide shots of an art style, search for `"{artist name}" close-up detail` or `"{art style}" character portrait`.
2. **Add new sources to the existing source list** — append to `sources.json` with a note like `"added_in": "iteration-2"` so you can track what came from which round.
3. **Download into the same `raw/` folder** using `--start-index` set to the actual file count in `raw/` (not an estimate). The dedup in the download script will catch any exact duplicates with existing images.
4. **Re-run Step 4** on the full dataset (old + new images) and re-score the diversity checklist.

Cap at 2-3 iteration rounds. After that, diminishing returns kick in — the user is better off training with what they have and doing a second LoRA training run if needed, rather than endlessly perfecting the dataset.

### Step 5: Process Images

Prepare the curated images for training. Use the target resolution from the user's base model choice (asked in the clarification interview):

| Base Model | Target Resolution |
|---|---|
| FLUX | 1024 |
| SDXL | 1024 |
| SD 1.5 | 512 |

#### Remove Rejected Images

Step 4 recommended removing some images. Either delete rejected files from `raw/`, or create a `keep.txt` (one filename per line) and pass it via `--keep-list`.

Run `scripts/prepare_dataset.py` with `--target-resolution` matching the base model (1024 for FLUX/SDXL, 512 for SD 1.5). Read `references/scripts-reference.md` before running — it has the full flag reference, resolution bucket tables, and upscaling warnings.

The script resizes to resolution buckets, converts to PNG, strips metadata, and writes `processing-report.json`. It warns if any image needs >2x upscale — consider replacing those with higher-res versions or pre-upscaling with Real-ESRGAN.

### Step 6: Auto-Caption Images

Generate captions following the lora-training skill's captioning strategy. This step has three parts: choose the trigger word, run auto-captioning, and clean up the results.

#### Choose Mode and Trigger Word

The **mode** maps directly to the user's answer from the clarification interview ("What should the LoRA learn?"):

| User wants to learn... | Mode | Caption format |
|---|---|---|
| An art style / aesthetic | `style` | `{trigger_word} style, {description of content}` |
| A specific person / character | `subject` | `{trigger_word}, {description of everything except the subject}` |
| A type of object / product | `object` | `{trigger_word}, {description of context and setting}` |

The **trigger word** is what activates the LoRA during inference. Good trigger words are:
- Short and memorable (1-2 words, e.g., `amanoart`, `cyberpunkanime`)
- Unique enough that they don't collide with existing tokens the model already knows (avoid common English words)
- Descriptive enough that the user will remember what they do
- Lowercase, no spaces (underscores OK: `vintage_kb`)

Suggest a trigger word to the user and let them confirm or pick their own. If they already specified one, use it.

#### Run Auto-Captioning

Run `scripts/auto_caption.py` with the trigger word and mode. Default captioner is Florence-2 (good all-rounder); use WD14 for anime, BLIP-2 for premium realistic photos. Read `references/scripts-reference.md` before running — it has the full captioner comparison, timing expectations, and all CLI flags.

**WD14 output format**: WD14 produces comma-separated booru-style tags (e.g., `1girl, blue_hair, cityscape, neon_lights`), not natural-language descriptions like Florence-2 and BLIP-2. When showing sample captions from a WD14 run, present them as tag lists — don't rewrite them into prose. The tag format works well for training; it doesn't need conversion.

#### Caption Hygiene

The script auto-strips style-leaking words ("watercolor painting", "anime style", "beautiful", "masterpiece") because they teach the model to associate the trigger word with text tokens instead of visual features. Use `--extra-strip-words` for project-specific terms. See `references/scripts-reference.md` for the full blocklist.

The caption should describe **what's in the image** (subject, composition, colors, setting), not **how it was made**. The LoRA learns the "how" from the pixels; the caption teaches it what content to apply the style to.

#### Review Captions

Each caption is saved as a `.txt` file alongside its image (e.g., `001.png` and `001.txt`). After auto-captioning, present 3-5 example captions to the user so they can check for:
- Style-leaking words the blocklist missed — add these to `--extra-strip-words` and re-run
- Inaccurate descriptions (auto-captioners aren't perfect)
- Missing important details
- Consistency of format across captions

Auto-captions are a starting point — the user may want to edit some manually for better results.

### Step 7: Generate Dataset Report

Aggregate the pipeline's existing reports into a single manifest. Read these files to populate the report — do not guess values:

| Field | Source |
|---|---|
| Image count, resolution buckets | `processed/processing-report.json` |
| Captioning method, trigger word, mode | `processed/caption-report.json` |
| Source URLs and attribution | `download-log.json`, `extraction-log.json` |
| Source tiers | `sources.json` |
| Quality scorecard | Your Step 4 curation notes |

Build the manifest:

```json
{
  "project_name": "jrpg-art-style",
  "created": "2026-04-04T12:00:00Z",
  "target_architecture": "FLUX",
  "trigger_word": "jrpgart",
  "captioning_mode": "style",
  "captioning_method": "florence2",
  "caption_strip_words": ["final fantasy", "square enix"],
  "target_resolution": 1024,
  "image_count": 25,
  "resolution_buckets": {"1024x1024": 10, "1152x896": 8, "896x1152": 7},
  "sources_summary": {
    "tier_a": 3,
    "tier_b": 2,
    "total_urls": 40,
    "images_kept": 25,
    "video_frames_used": 8,
    "iterations": 1
  },
  "quality_scorecard": {
    "subject_variety": "PASS",
    "composition_range": "PASS",
    "color_distribution": "PASS",
    "background_variety": "PASS"
  },
  "dataset_path": "datasets/jrpg-art-style/processed/",
  "ready_for_training": true,
  "notes": "Focus on Amano-style watercolor JRPG illustrations. 25 images with Florence-2 captions."
}
```

Save to `datasets/{project-name}/dataset-report.json`.

The `notes` field is free-form — summarize what the dataset is for, any caveats (e.g., "3 images needed >2x upscale"), and anything the training skill should know.

### Step 8: Hand Off to Training

Present a summary to the user and point them to the training skill. Include the report path so the training skill can read settings automatically:

```
Dataset ready: datasets/{project-name}/processed/
  - {N} images across {bucket_count} resolution buckets
  - Captioned with {captioner} ({mode} mode)
  - Trigger word: {trigger_word}
  - Quality: all scorecard criteria PASS
  - Report: datasets/{project-name}/dataset-report.json

To start training, say:
  "Train a LoRA using the {project-name} dataset"

The training skill will read dataset-report.json to pick up your
trigger word, resolution, and captioning settings automatically.
```

If any scorecard criteria were WEAK (not FAIL — FAIL should have been resolved in Step 4b), mention them here so the user can decide whether to proceed or gather more data:

```
Note: "variety" scored WEAK — most images are front-facing portraits.
The LoRA may struggle with other poses. You can proceed, or gather
more varied images first.
```

## Dataset Folder Structure

Read `references/folder-structure.md` when setting up a new project. Key directories: `raw/` (originals), `processed/` (training-ready images + captions), plus JSON reports at each step.

## Ethical Considerations

When gathering training data from the web, keep these principles in mind:

- **Attribution**: Always log where each image came from (`download-log.json`). If the user plans to distribute or commercialize a trained LoRA, they should review the source licenses.
- **Respect robots.txt**: When manually browsing sources, check whether the site's robots.txt discourages scraping. The download script itself uses direct URLs and doesn't crawl.
- **Personal photos**: If gathering photos of real people, flag this to the user — training on someone's likeness without consent raises ethical concerns, especially for commercial use.
- **Watermarks**: Images with visible watermarks suggest the creator doesn't want free redistribution. Flag these during curation and let the user decide.

These aren't blockers — the user makes the final call. But surface the information so they can make informed decisions.

## Offline Mode

| Capability | Online | Offline |
|---|---|---|
| Web research & source discovery | Yes | No — need internet |
| Image downloading | Yes | No — need internet |
| Video downloading | Yes | No — need internet |
| Frame extraction from local video | N/A | Yes (ffmpeg is local) |
| Image processing & resizing | N/A | Yes (local scripts) |
| Auto-captioning | N/A | Yes (local models) |
| Dataset report generation | N/A | Yes |

In offline mode, the skill can process and prepare images the user already has locally, but cannot perform web research or downloads. If the user has raw images in a folder, skip to Step 5 (Process Images).
