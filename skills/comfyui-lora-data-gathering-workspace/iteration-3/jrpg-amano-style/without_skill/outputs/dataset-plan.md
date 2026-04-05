# Dataset Preparation Plan: Amano JRPG Watercolor LoRA

## Overview

**Goal**: Train a LoRA that captures the "Yoshitaka Amano Final Fantasy watercolor" aesthetic -- ethereal watercolor washes, fine calligraphic ink linework, elongated fantasy figures, and the JRPG concept art feel of the FF I-VI era.

**Target model**: SDXL (primary) or FLUX.1-dev (if available)
**Target dataset size**: 150-250 curated images at 1024x1024
**Trigger token**: `amano_watercolor` (or `yk_amano_style`)

---

## Phase 1: Image Acquisition

### Step 1A: Free Web Sources (Do First)

**Final Fantasy Wiki scraping with gallery-dl:**

```bash
# Install gallery-dl
pip install gallery-dl

# Download Amano artwork category from FF Wiki
gallery-dl "https://finalfantasy.fandom.com/wiki/Category:Yoshitaka_Amano_artwork" \
  --dest ./raw_downloads/ff-wiki/ \
  --filename "{category}_{num:04d}.{extension}"

# Also grab individual game art pages
gallery-dl "https://finalfantasy.fandom.com/wiki/Final_Fantasy/Artwork" --dest ./raw_downloads/ff-wiki/
gallery-dl "https://finalfantasy.fandom.com/wiki/Final_Fantasy_II/Artwork" --dest ./raw_downloads/ff-wiki/
gallery-dl "https://finalfantasy.fandom.com/wiki/Final_Fantasy_III/Artwork" --dest ./raw_downloads/ff-wiki/
gallery-dl "https://finalfantasy.fandom.com/wiki/Final_Fantasy_IV/Artwork" --dest ./raw_downloads/ff-wiki/
gallery-dl "https://finalfantasy.fandom.com/wiki/Final_Fantasy_V/Artwork" --dest ./raw_downloads/ff-wiki/
gallery-dl "https://finalfantasy.fandom.com/wiki/Final_Fantasy_VI/Artwork" --dest ./raw_downloads/ff-wiki/
```

**Square Enix press assets (manual):**
- Visit https://press.na.square-enix.com/
- Search for "Final Fantasy Pixel Remaster", "Final Fantasy anniversary"
- Download any Amano key art at highest available resolution

**Archive.org check:**
```bash
# Search for digitized Amano art books
# Manual review needed -- check https://archive.org/search?query=yoshitaka+amano
# Download relevant pages as high-res images
```

### Step 1B: Art Book Scanning (If Budget Allows)

**Recommended scanning setup:**
- Scanner: Flatbed scanner at **600 DPI minimum** (1200 DPI ideal)
- Format: **TIFF or PNG** (lossless -- never scan to JPEG)
- Color space: **sRGB** (for consistency with digital training pipelines)
- Scan each page flat, centered, with book spine gently pressed

**Scanning commands (using a scanner with CLI support, e.g., SANE on Linux):**
```bash
# Example with scanimage (SANE)
scanimage --resolution 600 --mode Color --format=tiff \
  -x 297 -y 420 > scan_page_001.tiff

# Or on Windows with NAPS2 CLI:
naps2 --output "scan_{n:D4}.tiff" --dpi 600 --source flatbed
```

**Post-scan cleanup:**
```bash
# Convert TIFF to PNG for easier handling
mogrify -format png *.tiff

# Auto-crop white borders (ImageMagick)
for f in *.png; do
  convert "$f" -fuzz 5% -trim +repage "cropped_$f"
done
```

**Priority scanning order:**
1. The Sky Vol. 1 (FF I-III) -- core classic period
2. The Sky Vol. 2 (FF IV-VI) -- peak watercolor period
3. Dawn -- character studies
4. Vampire Hunter D covers -- dark fantasy variety

### Step 1C: Video Frame Extraction (Last Resort Only)

Only if you cannot reach 80+ images from Steps 1A and 1B.

```bash
# Extract keyframes from an exhibition walkthrough video
ffmpeg -i exhibition_video.mp4 \
  -vf "select='eq(pict_type,I)',scale=iw:ih" \
  -vsync vfr \
  ./raw_downloads/video_frames/frame_%04d.png

# Alternative: extract frames at 1 per 5 seconds for art showcases
ffmpeg -i art_showcase.mp4 \
  -vf "fps=1/5" \
  ./raw_downloads/video_frames/frame_%04d.png
```

**Video frame quality check**: Manually review ALL extracted frames. Reject any with:
- Motion blur
- Perspective distortion (camera at angle to artwork)
- Glass reflections or glare
- People or objects partially blocking the art
- Compression artifacts

---

## Phase 2: Curation and Deduplication

### Step 2A: Initial Sort

Create the following directory structure:
```
dataset/
  raw/                 # Everything downloaded
  curated/
    accept/            # Images that pass quality check
    reject/            # Images that fail quality check
    maybe/             # Borderline -- review later
  processed/           # Final training-ready images
  captions/            # Caption text files
```

### Step 2B: Quality Filter -- Manual Pass

Go through every image in `raw/` and sort into accept/reject/maybe. Apply these criteria:

**Accept if ALL of these are true:**
- [x] Artwork is by Yoshitaka Amano (not fan art, not style imitation)
- [x] In the target watercolor+ink style (not pencil sketches, not digital paintings, not metallic-leaf-heavy)
- [x] Resolution >= 768px on shortest edge
- [x] No significant scan artifacts (moire, color banding, heavy halftone dots)
- [x] No heavy JPEG compression artifacts
- [x] Complete or near-complete composition (not a tiny crop of a larger work)
- [x] Color appears reasonably accurate (not obviously wrong white balance)

**Reject if ANY of these are true:**
- [ ] Fan art or uncertain attribution
- [ ] Resolution < 512px on shortest edge
- [ ] Pencil sketch or rough draft (unless deliberately including sketches)
- [ ] Primarily metallic/gold leaf work (won't translate to 2D generation)
- [ ] Photographs of art with visible camera distortion
- [ ] Duplicate of an already-accepted image at lower quality

### Step 2C: Deduplication

```bash
# Install duplicate finder
pip install imagededup

# Python script for deduplication
python3 << 'PYEOF'
from imagededup.methods import PHash
phasher = PHash()
encodings = phasher.encode_images(image_dir="dataset/curated/accept/")
duplicates = phasher.find_duplicates(encoding_map=encodings, max_distance_threshold=10)

# Print duplicate groups
for key, dupes in duplicates.items():
    if dupes:
        print(f"DUPLICATE GROUP: {key} <-> {dupes}")
PYEOF
```

For each duplicate group, keep only the highest resolution / cleanest version. Move the rest to `reject/`.

### Step 2D: Dataset Balance Check

After curation, verify the dataset has good variety:

| Category | Target % | Min Images |
|----------|----------|------------|
| Single character portraits | 30-40% | 45-100 |
| Full-body character art | 20-30% | 30-75 |
| Multi-character compositions | 10-15% | 15-35 |
| Landscapes / environments | 5-10% | 8-25 |
| Abstract / decorative pieces | 5-10% | 8-25 |
| Close-up details (faces, hands) | 5-10% | 8-25 |

If any category is severely underrepresented, go back to acquisition and target that gap.

---

## Phase 3: Image Processing

### Step 3A: Resolution Standardization

All images must be prepared for training at the model's native resolution.

**For SDXL LoRA (1024x1024):**

```bash
# Using ImageMagick -- resize and pad to square
# Preserve aspect ratio, pad with white (matches Amano's paper color)
for f in dataset/curated/accept/*.png; do
  basename=$(basename "$f")
  convert "$f" \
    -resize 1024x1024^ \
    -gravity center \
    -extent 1024x1024 \
    -background white \
    "dataset/processed/${basename}"
done
```

**Better approach -- bucket resizing for aspect-ratio-aware training:**

Most modern LoRA training tools (kohya_ss, ai-toolkit) support aspect ratio bucketing. In that case, just ensure minimum resolution:

```bash
# Resize so shortest edge is at least 1024px, keep aspect ratio
for f in dataset/curated/accept/*.png; do
  basename=$(basename "$f")
  convert "$f" \
    -resize "1024x1024^" \
    -quality 100 \
    "dataset/processed/${basename}"
done
```

**For FLUX LoRA (1024x1024 or 512x512 depending on trainer):**

```bash
# Same approach, but FLUX trainers may want different bucket sizes
# ai-toolkit typically handles bucketing automatically
# Just ensure shortest edge >= 512px (768+ preferred)
for f in dataset/curated/accept/*.png; do
  basename=$(basename "$f")
  convert "$f" \
    -resize "768x768^" \
    -quality 100 \
    "dataset/processed/${basename}"
done
```

### Step 3B: Color Consistency Check

```bash
# Check for grayscale images accidentally included
python3 << 'PYEOF'
from PIL import Image
import os

processed_dir = "dataset/processed"
for fname in os.listdir(processed_dir):
    if not fname.lower().endswith(('.png', '.jpg', '.jpeg')):
        continue
    img = Image.open(os.path.join(processed_dir, fname))
    if img.mode != 'RGB':
        print(f"NON-RGB: {fname} (mode: {img.mode})")
    # Check if image is effectively grayscale
    if img.mode == 'RGB':
        r, g, b = img.split()
        from itertools import combinations
        diff = sum(abs(a - b) for a, b in [(r.histogram(), g.histogram())])
        # Simple heuristic -- detailed check would use numpy
    print(f"OK: {fname} ({img.size[0]}x{img.size[1]}, {img.mode})")
PYEOF

# Convert all to RGB PNG for consistency
for f in dataset/processed/*; do
  convert "$f" -colorspace sRGB -type TrueColor "dataset/processed/$(basename $f .jpg).png"
done
```

### Step 3C: Optional Upscaling for Low-Res Images

For images between 512px-768px that you want to keep:

```bash
# Using Real-ESRGAN for 2x upscale (install realesrgan-ncnn-vulkan)
realesrgan-ncnn-vulkan -i low_res_image.png -o upscaled_image.png -n realesrgan-x4plus-anime -s 2

# Or through ComfyUI if running -- build an upscale workflow
# Or use Python with spandrel/BasicSR
```

**Caution**: Upscaled images can introduce artifacts that the LoRA learns. Use sparingly and only for otherwise-excellent images that are slightly below resolution threshold.

---

## Phase 4: Captioning

### Step 4A: Captioning Strategy

Use **natural language captions** (not tag-based), as this works best for SDXL and FLUX LoRAs.

**Caption structure:**
```
[trigger_token], [medium/style description], [subject description], [composition details], [color palette], [mood/atmosphere]
```

**Trigger token**: `amano_watercolor` -- appears in EVERY caption to anchor the style.

### Step 4B: Auto-Captioning with WD Tagger + Manual Refinement

```bash
# Step 1: Generate initial captions with BLIP-2 or CogVLM
# Using kohya_ss caption tool:
python caption_with_blip2.py \
  --input_dir dataset/processed/ \
  --output_dir dataset/captions/ \
  --model blip2 \
  --prefix "amano_watercolor, "

# OR use WD14 Tagger for tag-based initial pass:
python tag_images_by_wd14_tagger.py \
  --input_dir dataset/processed/ \
  --output_dir dataset/captions/ \
  --model wd-v1-4-moat-tagger-v2 \
  --thresh 0.35
```

**Step 2: Convert tags to natural language (Python script):**

```python
import os
import re

TRIGGER = "amano_watercolor"
STYLE_PREFIX = "watercolor and ink illustration in the style of Yoshitaka Amano"

MEDIUM_TAGS = {
    "watercolor_(medium)", "ink_(medium)", "traditional_media",
    "painting_(medium)", "illustration"
}
DISCARD_TAGS = {
    "absurdres", "highres", "scan", "official_art", "game_cg",
    "artist_name", "copyright_name", "character_name"
}

caption_dir = "dataset/captions"
for fname in os.listdir(caption_dir):
    if not fname.endswith(".txt"):
        continue
    with open(os.path.join(caption_dir, fname)) as f:
        tags = [t.strip() for t in f.read().split(",")]

    # Filter out meta tags
    tags = [t for t in tags if t not in MEDIUM_TAGS and t not in DISCARD_TAGS]

    # Build natural language caption
    caption = f"{TRIGGER}, {STYLE_PREFIX}, {', '.join(tags)}"

    with open(os.path.join(caption_dir, fname), "w") as f:
        f.write(caption)
```

**Step 3: Manual caption refinement (CRITICAL)**

Auto-captions are a starting point. You MUST manually review and edit every caption to:
- Ensure the style description is accurate for that specific image
- Add Amano-specific details the tagger misses (e.g., "flowing calligraphic linework", "wet-on-wet watercolor blooms")
- Correct any misidentified subjects
- Add character names where known (e.g., "Terra Branford", "Cecil Harvey")
- Describe the color palette specifically
- Remove any hallucinated or incorrect tags

### Step 4C: Caption File Format

Each image gets a matching `.txt` file with the same name:

```
dataset/processed/ff6_terra_01.png
dataset/captions/ff6_terra_01.txt
```

For kohya_ss training, captions go in the same directory as images:
```
dataset/training/
  ff6_terra_01.png
  ff6_terra_01.txt
  ff4_cecil_01.png
  ff4_cecil_01.txt
  ...
```

See `sample-captions.md` for detailed caption examples.

---

## Phase 5: Dataset Organization for Training

### Step 5A: Directory Structure (kohya_ss Format)

```
training_data/
  img/
    20_amano_watercolor/     # repeats_[trigger]
      image001.png
      image001.txt
      image002.png
      image002.txt
      ...
  reg/                       # regularization images (optional but recommended)
    1_watercolor_illustration/
      reg001.png
      reg001.txt
      ...
```

**Repeat count**: `20` means each image is seen 20 times per epoch. Adjust based on dataset size:
- 100-150 images: use 15-20 repeats
- 150-250 images: use 10-15 repeats
- 250+ images: use 5-10 repeats

### Step 5B: Regularization Images

Regularization images prevent the model from associating ALL watercolor art with the trigger token. They represent "generic watercolor illustration" that the model should NOT change.

**Sources for regularization images:**
- Generate 200-500 images from the base model using prompts like:
  - "watercolor illustration of a fantasy character"
  - "ink and watercolor painting, ethereal atmosphere"
  - "traditional media fantasy art, detailed illustration"

```bash
# Generate reg images with ComfyUI or via diffusers
python generate_reg_images.py \
  --prompt "watercolor illustration of a fantasy character, traditional media" \
  --num_images 300 \
  --output_dir training_data/reg/1_watercolor_illustration/
```

### Step 5C: Final Validation Script

```python
"""Validate the complete dataset before training."""
import os
from PIL import Image

TRAINING_DIR = "training_data/img/20_amano_watercolor"
MIN_SIZE = 768
EXPECTED_FORMAT = "RGB"

errors = []
stats = {"total": 0, "with_caption": 0, "min_width": 99999, "min_height": 99999}

for fname in os.listdir(TRAINING_DIR):
    if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        continue
    stats["total"] += 1
    fpath = os.path.join(TRAINING_DIR, fname)

    # Check image
    img = Image.open(fpath)
    w, h = img.size
    stats["min_width"] = min(stats["min_width"], w)
    stats["min_height"] = min(stats["min_height"], h)

    if min(w, h) < MIN_SIZE:
        errors.append(f"TOO SMALL: {fname} ({w}x{h})")
    if img.mode != EXPECTED_FORMAT:
        errors.append(f"WRONG MODE: {fname} ({img.mode})")

    # Check caption
    caption_path = os.path.splitext(fpath)[0] + ".txt"
    if os.path.exists(caption_path):
        stats["with_caption"] += 1
        with open(caption_path) as f:
            caption = f.read().strip()
        if not caption.startswith("amano_watercolor"):
            errors.append(f"MISSING TRIGGER: {fname}")
        if len(caption) < 20:
            errors.append(f"SHORT CAPTION: {fname} ({len(caption)} chars)")
    else:
        errors.append(f"NO CAPTION: {fname}")

print(f"=== Dataset Validation Report ===")
print(f"Total images: {stats['total']}")
print(f"With captions: {stats['with_caption']}")
print(f"Min dimensions: {stats['min_width']}x{stats['min_height']}")
print(f"Errors: {len(errors)}")
for e in errors:
    print(f"  - {e}")

if not errors:
    print("DATASET READY FOR TRAINING")
else:
    print("FIX ERRORS BEFORE TRAINING")
```

---

## Phase 6: Training Configuration (Handoff)

### Recommended kohya_ss Settings for SDXL LoRA

```toml
[training]
pretrained_model_name_or_path = "stabilityai/stable-diffusion-xl-base-1.0"
train_data_dir = "training_data/img"
reg_data_dir = "training_data/reg"
output_dir = "output/amano_watercolor_lora"
output_name = "amano_watercolor_v1"

resolution = 1024
train_batch_size = 1
max_train_epochs = 10
learning_rate = 1e-4
unet_lr = 1e-4
text_encoder_lr = 5e-5
lr_scheduler = "cosine_with_restarts"
lr_warmup_steps = 100

network_module = "networks.lora"
network_dim = 32
network_alpha = 16

mixed_precision = "bf16"
save_precision = "bf16"
save_every_n_epochs = 2
optimizer_type = "AdamW8bit"
max_token_length = 225
bucket_reso_steps = 64
min_bucket_reso = 512
max_bucket_reso = 2048
enable_bucket = true
cache_latents = true
gradient_checkpointing = true
```

### Recommended ai-toolkit Settings for FLUX LoRA

```yaml
config:
  name: "amano_watercolor_flux"
  process:
    - type: "sd_trainer"
      training_folder: "training_data/img/20_amano_watercolor"
      output:
        save_every: 250
        dtype: "bf16"
      model:
        name_or_path: "black-forest-labs/FLUX.1-dev"
        type: "flux"
      train:
        batch_size: 1
        steps: 2500
        gradient_accumulation_steps: 1
        lr: 4e-4
        optimizer: "adamw8bit"
      network:
        type: "lora"
        rank: 16
        alpha: 16
      trigger_word: "amano_watercolor"
```

---

## Pipeline Summary Checklist

- [ ] **Phase 1**: Download from FF Wiki, check press kits, scan art books if purchased
- [ ] **Phase 2**: Manual quality sort, deduplication, balance check
- [ ] **Phase 3**: Resize to training resolution, color consistency, optional upscaling
- [ ] **Phase 4**: Auto-caption then manual refinement with trigger token
- [ ] **Phase 5**: Organize into kohya/ai-toolkit directory structure with regularization
- [ ] **Phase 6**: Configure training parameters and begin training
- [ ] **Post-training**: Test with prompts, iterate on dataset/captions if results are off
