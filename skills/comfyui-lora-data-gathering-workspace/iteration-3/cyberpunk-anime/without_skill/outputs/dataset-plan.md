# Dataset Plan: Cyberpunk Anime Style LoRA (SDXL)

## Overview

- **LoRA Type**: Style LoRA
- **Base Model**: SDXL 1.0
- **Trigger Word**: `cpanime`
- **Target Dataset Size**: 150-250 images
- **Target Resolution**: 1024x1024 (with SDXL bucketing for varied aspect ratios)
- **Caption Format**: Natural language with trigger word prefix

---

## Phase 1: Research & Source Identification (Complete)

See `research-report.md` and `sources.json` for full details.

**Summary of sources**:
- Primary: Blu-ray frame extraction from Ghost in the Shell (1995), Akira (1988), GitS:SAC
- Secondary: Art book scans, Danbooru/Safebooru official art
- Tertiary: Selective use of related titles (Psycho-Pass, Bubblegum Crisis) and curated fan art

---

## Phase 2: Image Acquisition

### Step 2a: Video Frame Extraction

**Prerequisites**:
- ffmpeg installed (`winget install ffmpeg` or download from https://ffmpeg.org)
- Personal Blu-ray/DVD copies ripped to MKV (use MakeMKV for personal backups)
- Sufficient disk space (~5-10 GB for raw frame dumps per film)

**Commands**:

```bash
# Create working directories
mkdir -p dataset/raw/{gits-1995,akira,gits-sac,psycho-pass,bubblegum-crisis}

# Ghost in the Shell (1995) - extract 1 frame every 3 seconds
ffmpeg -i "Ghost_in_the_Shell_1995.mkv" \
  -vf "fps=1/3,scale=-1:1080:flags=lanczos" \
  -q:v 1 -start_number 1 \
  dataset/raw/gits-1995/gits_%05d.png

# Akira (1988) - extract 1 frame every 3 seconds
ffmpeg -i "Akira_1988.mkv" \
  -vf "fps=1/3,scale=-1:1080:flags=lanczos" \
  -q:v 1 -start_number 1 \
  dataset/raw/akira/akira_%05d.png

# GitS: SAC - extract 1 frame every 5 seconds (series has more downtime)
# Run per-episode, e.g.:
for i in $(seq -w 1 26); do
  ffmpeg -i "SAC_S1_E${i}.mkv" \
    -vf "fps=1/5,scale=-1:1080:flags=lanczos" \
    -q:v 1 -start_number 1 \
    dataset/raw/gits-sac/sac_s1e${i}_%05d.png
done

# Psycho-Pass - selective episodes only (1, 11, 16, 22)
for ep in 01 11 16 22; do
  ffmpeg -i "PsychoPass_E${ep}.mkv" \
    -vf "fps=1/5,scale=-1:1080:flags=lanczos" \
    -q:v 1 -start_number 1 \
    dataset/raw/psycho-pass/pp_e${ep}_%05d.png
done
```

**Expected raw output**: 2000-5000+ frames total (will be heavily culled in curation).

### Step 2b: Subtitle Removal from Screencaps

If your video source has hardcoded subtitles:

```bash
# Option A: Crop bottom 12% of frame (quick and dirty)
# For 1080p: crop 130px from bottom
ffmpeg -i input.mkv \
  -vf "fps=1/3,crop=in_w:in_h-130:0:0,scale=-1:1080:flags=lanczos" \
  -q:v 1 output_%05d.png

# Option B: Use subtitle-free audio track (preferred)
# List audio/subtitle streams first:
ffmpeg -i input.mkv
# Then select the Japanese audio without subtitle overlay - most Blu-rays
# have separate subtitle tracks that aren't burned in.
```

### Step 2c: Image Board Downloads

**Install gallery-dl**:
```bash
pip install gallery-dl
```

**Download commands**:
```bash
# Danbooru - Ghost in the Shell official art, high resolution
gallery-dl "https://danbooru.donmai.us/posts?tags=ghost_in_the_shell+official_art+highres" \
  -d dataset/raw/danbooru-gits/ \
  --filter "width >= 1024 and height >= 768"

# Danbooru - Akira official art
gallery-dl "https://danbooru.donmai.us/posts?tags=akira_%28manga%29+highres" \
  -d dataset/raw/danbooru-akira/ \
  --filter "width >= 1024 and height >= 768"

# Danbooru - Cyberpunk cityscapes
gallery-dl "https://danbooru.donmai.us/posts?tags=cyberpunk+cityscape+highres" \
  -d dataset/raw/danbooru-cyberpunk/ \
  --filter "width >= 1024 and height >= 768"

# Safebooru - Neon cyberpunk night scenes
gallery-dl "https://safebooru.donmai.us/posts?tags=cyberpunk+neon_lights+night+highres" \
  -d dataset/raw/safebooru/
```

### Step 2d: Art Book Scanning (Manual)

If you have physical art books:
1. Use a flatbed scanner at **300 DPI minimum** (600 DPI for smaller illustrations)
2. Scan as **TIFF or PNG** (lossless)
3. Correct for page curvature using GIMP/Photoshop lens correction
4. Crop to individual illustrations (remove page margins, text, page numbers)
5. Save to `dataset/raw/artbooks/`

---

## Phase 3: Curation

This is the most labor-intensive and important phase. Quality of curation directly determines LoRA quality.

### Step 3a: First-Pass Automated Filtering

**Remove near-duplicates with imagededup**:
```bash
pip install imagededup

python -c "
from imagededup.methods import PHash
phasher = PHash()
# Find duplicates in the raw frames directory
duplicates = phasher.find_duplicates(
    image_dir='dataset/raw/gits-1995',
    max_distance_threshold=10
)
# Print files to remove
for key, dupes in duplicates.items():
    for d in dupes:
        print(d)
" > duplicates_to_remove.txt
```

**Remove low-quality images (blurry, dark, featureless)**:
```python
# quality_filter.py
import cv2
import os
import shutil

def laplacian_variance(image_path):
    """Higher = sharper. Threshold ~100 for anime."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0
    return cv2.Laplacian(img, cv2.CV_64F).var()

def mean_brightness(image_path):
    """Filter out near-black frames."""
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return 0
    return img.mean()

input_dir = "dataset/raw/gits-1995"
reject_dir = "dataset/rejected/gits-1995"
os.makedirs(reject_dir, exist_ok=True)

for fname in os.listdir(input_dir):
    path = os.path.join(input_dir, fname)
    sharpness = laplacian_variance(path)
    brightness = mean_brightness(path)
    
    if sharpness < 80 or brightness < 20 or brightness > 245:
        shutil.move(path, os.path.join(reject_dir, fname))
        print(f"REJECTED: {fname} (sharpness={sharpness:.0f}, brightness={brightness:.0f})")
```

### Step 3b: Manual Curation (Critical)

After automated filtering, manually review remaining images. Use a fast image viewer (IrfanView, XnView, or `feh` on Linux).

**Selection criteria -- KEEP**:
- [x] Establishing city shots showing the megacity environment
- [x] Character medium/wide shots with environmental context
- [x] Technology close-ups (cybernetics, holographic UI, vehicles)
- [x] Atmospheric shots (rain, neon reflections, fog, steam)
- [x] Action sequences with clear composition (not motion-blurred)
- [x] Interior environments (labs, bars, offices with cyberpunk aesthetics)
- [x] Mechanical design showcases (Tachikoma, Kaneda's bike, powered armor)

**Selection criteria -- REJECT**:
- [ ] Pure black/white/single-color frames
- [ ] Extreme close-ups (just an eye, mouth, etc.) -- no style context
- [ ] Heavily motion-blurred frames
- [ ] Frames with visible subtitle text
- [ ] Conversation shots with plain backgrounds
- [ ] Frames that look generic (could be any anime, nothing cyberpunk-specific)
- [ ] Frames with visible compression artifacts

**Target**: Reduce raw extraction (2000-5000 frames) down to 150-250 curated images.

### Step 3c: Category Balance Check

Aim for this approximate distribution in the final dataset:

| Category | Target % | Count (of 200) |
|---|---|---|
| Cityscapes / environment wide shots | 25% | ~50 |
| Character + environment (medium shots) | 25% | ~50 |
| Technology / mechanical close-ups | 15% | ~30 |
| Atmospheric / mood shots | 15% | ~30 |
| Action sequences | 10% | ~20 |
| Interior environments | 10% | ~20 |

If any category is underrepresented, go back to the raw frames or supplement from image board sources.

---

## Phase 4: Image Processing

### Step 4a: Resolution Standardization

SDXL training uses **aspect ratio bucketing** -- images don't need to be square, but they need to meet minimum resolution requirements.

**SDXL Standard Bucket Resolutions**:
- 1024x1024 (1:1)
- 1152x896 (~4:3 landscape)
- 896x1152 (~3:4 portrait)
- 1216x832 (~3:2 landscape)
- 832x1216 (~2:3 portrait)
- 1344x768 (~16:9 landscape)
- 768x1344 (~9:16 portrait)
- 1536x640 (ultra-wide)

**Processing script**:
```python
# resize_for_sdxl.py
from PIL import Image
import os

SDXL_BUCKETS = [
    (1024, 1024), (1152, 896), (896, 1152),
    (1216, 832), (832, 1216), (1344, 768),
    (768, 1344), (1536, 640), (640, 1536)
]

def find_best_bucket(w, h):
    """Find the SDXL bucket that best matches the image's aspect ratio."""
    aspect = w / h
    best = min(SDXL_BUCKETS, key=lambda b: abs(b[0]/b[1] - aspect))
    return best

def process_image(input_path, output_path):
    img = Image.open(input_path)
    w, h = img.size
    
    # Skip images that are too small
    if min(w, h) < 768:
        print(f"SKIP (too small): {input_path} ({w}x{h})")
        return False
    
    bucket_w, bucket_h = find_best_bucket(w, h)
    
    # Resize to fit bucket (maintain aspect, then center-crop to exact bucket)
    img_ratio = w / h
    bucket_ratio = bucket_w / bucket_h
    
    if img_ratio > bucket_ratio:
        # Image is wider -- fit height, crop width
        new_h = bucket_h
        new_w = int(bucket_h * img_ratio)
    else:
        # Image is taller -- fit width, crop height
        new_w = bucket_w
        new_h = int(bucket_w / img_ratio)
    
    img = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Center crop to exact bucket dimensions
    left = (new_w - bucket_w) // 2
    top = (new_h - bucket_h) // 2
    img = img.crop((left, top, left + bucket_w, top + bucket_h))
    
    img.save(output_path, "PNG")
    print(f"OK: {input_path} -> {bucket_w}x{bucket_h}")
    return True

# Process all curated images
input_dir = "dataset/curated"
output_dir = "dataset/processed"
os.makedirs(output_dir, exist_ok=True)

for fname in os.listdir(input_dir):
    if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        process_image(
            os.path.join(input_dir, fname),
            os.path.join(output_dir, os.path.splitext(fname)[0] + ".png")
        )
```

### Step 4b: Upscaling (If Needed)

For images below 1024px that are too good to discard (e.g., Bubblegum Crisis DVD sources):

```bash
# Install Real-ESRGAN
pip install realesrgan

# Upscale 2x with anime-specific model
python -m realesrgan -i dataset/low_res/ -o dataset/upscaled/ \
  -n realesr-animevideov3 -s 2
```

Alternative: Use the `4x-AnimeSharp` or `RealESRGAN_x4plus_anime_6B` model in ComfyUI for upscaling if ComfyUI is available.

### Step 4c: Final Quality Check

After processing, verify:
```python
# verify_dataset.py
from PIL import Image
import os

processed_dir = "dataset/processed"
issues = []

for fname in os.listdir(processed_dir):
    if not fname.endswith('.png'):
        continue
    path = os.path.join(processed_dir, fname)
    img = Image.open(path)
    w, h = img.size
    
    # Check minimum resolution
    if min(w, h) < 768:
        issues.append(f"TOO SMALL: {fname} ({w}x{h})")
    
    # Check for valid SDXL bucket
    if (w, h) not in [(1024,1024),(1152,896),(896,1152),(1216,832),
                       (832,1216),(1344,768),(768,1344),(1536,640),(640,1536)]:
        issues.append(f"NON-STANDARD SIZE: {fname} ({w}x{h})")
    
    # Check file size (suspiciously small = likely corrupt)
    fsize = os.path.getsize(path)
    if fsize < 50000:  # <50KB for 1024+ image is suspicious
        issues.append(f"SUSPICIOUS SIZE: {fname} ({fsize} bytes)")

if issues:
    print(f"Found {len(issues)} issues:")
    for i in issues:
        print(f"  - {i}")
else:
    print(f"All {len(os.listdir(processed_dir))} images pass validation.")
```

---

## Phase 5: Captioning

### Step 5a: Auto-Captioning with Florence-2

```python
# auto_caption.py
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import os
import torch

model_id = "microsoft/Florence-2-large"
processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(model_id, trust_remote_code=True).to("cuda")

image_dir = "dataset/processed"
caption_dir = "dataset/captions"
os.makedirs(caption_dir, exist_ok=True)

for fname in sorted(os.listdir(image_dir)):
    if not fname.endswith('.png'):
        continue
    
    img = Image.open(os.path.join(image_dir, fname)).convert("RGB")
    
    # Generate detailed caption
    prompt = "<MORE_DETAILED_CAPTION>"
    inputs = processor(text=prompt, images=img, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=200,
            num_beams=3
        )
    
    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    # Save caption as .txt file matching the image filename
    caption_path = os.path.join(caption_dir, fname.replace('.png', '.txt'))
    with open(caption_path, 'w') as f:
        f.write(caption)
    
    print(f"Captioned: {fname}")
```

### Step 5b: WD Tagger for Supplementary Tags

```python
# wd_tag.py  (using the onnx version)
# pip install onnxruntime-gpu pillow numpy pandas
import onnxruntime as ort
import numpy as np
from PIL import Image
import pandas as pd
import os

# Download wd-v1-4-vit-tagger-v2 ONNX model from HuggingFace
# Place model.onnx and selected_tags.csv in ./wd-tagger/

session = ort.InferenceSession("wd-tagger/model.onnx")
tags_df = pd.read_csv("wd-tagger/selected_tags.csv")

def predict_tags(image_path, threshold=0.35):
    img = Image.open(image_path).convert("RGB").resize((448, 448))
    img_array = np.array(img).astype(np.float32) / 255.0
    img_array = np.expand_dims(img_array, 0)
    
    probs = session.run(None, {session.get_inputs()[0].name: img_array})[0][0]
    
    results = []
    for i, prob in enumerate(probs):
        if prob > threshold and i < len(tags_df):
            results.append((tags_df.iloc[i]['name'], prob))
    
    return sorted(results, key=lambda x: -x[1])

# Generate tag files alongside captions
for fname in os.listdir("dataset/processed"):
    if not fname.endswith('.png'):
        continue
    tags = predict_tags(f"dataset/processed/{fname}")
    tag_str = ", ".join([t[0] for t in tags])
    with open(f"dataset/tags/{fname.replace('.png', '.tags.txt')}", 'w') as f:
        f.write(tag_str)
```

### Step 5c: Manual Caption Refinement

This is essential. Auto-captioners miss style-specific attributes.

**Refinement process**:
1. Open each image alongside its auto-caption
2. Prepend the trigger word `cpanime`
3. Add style-specific details the auto-captioner missed:
   - Lighting type (neon, rim lighting, volumetric)
   - Atmosphere (rain, fog, steam, haze)
   - Color palette descriptions
   - "anime style", "detailed background", "cyberpunk"
4. Remove incorrect or irrelevant auto-caption content
5. Keep captions 30-75 words (not too short, not too long)

**Tools for batch review**:
- **BooruDatasetTagManager**: GUI tool for reviewing images + editing captions
- **Stable Diffusion Dataset Tag Editor** (Automatic1111 extension): Web UI for caption editing
- **dataset-tag-editor** (standalone): Lightweight option

**Save final captions as `.txt` files with the same base name as images**:
```
dataset/processed/gits_00142.png
dataset/processed/gits_00142.txt    <-- caption file
```

---

## Phase 6: Dataset Validation & Report

### Step 6a: Generate Dataset Report

```python
# dataset_report.py
from PIL import Image
import os
import json
from collections import Counter

dataset_dir = "dataset/processed"
report = {
    "total_images": 0,
    "resolution_distribution": Counter(),
    "aspect_ratios": Counter(),
    "avg_caption_length": 0,
    "caption_word_count_range": [999, 0],
    "source_distribution": Counter(),
    "has_trigger_word": 0,
    "missing_captions": [],
    "file_size_stats": {"min": float('inf'), "max": 0, "total": 0}
}

caption_lengths = []

for fname in sorted(os.listdir(dataset_dir)):
    if not fname.endswith('.png'):
        continue
    
    report["total_images"] += 1
    
    # Image stats
    img = Image.open(os.path.join(dataset_dir, fname))
    w, h = img.size
    report["resolution_distribution"][f"{w}x{h}"] += 1
    report["aspect_ratios"][f"{w/h:.2f}"] += 1
    
    fsize = os.path.getsize(os.path.join(dataset_dir, fname))
    report["file_size_stats"]["min"] = min(report["file_size_stats"]["min"], fsize)
    report["file_size_stats"]["max"] = max(report["file_size_stats"]["max"], fsize)
    report["file_size_stats"]["total"] += fsize
    
    # Source tracking (from filename prefix)
    prefix = fname.split("_")[0]
    report["source_distribution"][prefix] += 1
    
    # Caption stats
    caption_file = os.path.join(dataset_dir, fname.replace('.png', '.txt'))
    if os.path.exists(caption_file):
        with open(caption_file) as f:
            caption = f.read().strip()
        words = len(caption.split())
        caption_lengths.append(words)
        report["caption_word_count_range"][0] = min(report["caption_word_count_range"][0], words)
        report["caption_word_count_range"][1] = max(report["caption_word_count_range"][1], words)
        if "cpanime" in caption:
            report["has_trigger_word"] += 1
    else:
        report["missing_captions"].append(fname)

if caption_lengths:
    report["avg_caption_length"] = sum(caption_lengths) / len(caption_lengths)

# Convert Counters to dicts for JSON
report["resolution_distribution"] = dict(report["resolution_distribution"])
report["aspect_ratios"] = dict(report["aspect_ratios"])
report["source_distribution"] = dict(report["source_distribution"])
report["file_size_stats"]["avg"] = report["file_size_stats"]["total"] / max(report["total_images"], 1)

with open("dataset/dataset_report.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
```

### Step 6b: Validation Checks

Before proceeding to training, verify:

- [ ] All images have matching `.txt` caption files
- [ ] All captions contain the trigger word `cpanime`
- [ ] No duplicate images (run perceptual hash check again)
- [ ] Resolution distribution matches SDXL bucket sizes
- [ ] No images below 768px on shortest side
- [ ] Category balance is roughly maintained
- [ ] No watermarks, subtitles, or artifacts visible (spot-check 10%)
- [ ] Total dataset size is in the 150-250 range
- [ ] File format is consistently PNG

---

## Phase 7: Training Handoff

### Directory Structure for Training

```
dataset/
  processed/
    gits_00001.png
    gits_00001.txt
    gits_00042.png
    gits_00042.txt
    akira_00003.png
    akira_00003.txt
    ...
  dataset_report.json
```

### Recommended SDXL LoRA Training Configuration

**Training tool**: [kohya-ss/sd-scripts](https://github.com/kohya-ss/sd-scripts) or [bmaltais/kohya_ss](https://github.com/bmaltais/kohya_ss) (GUI wrapper)

**Key parameters for a style LoRA**:

```toml
# training_config.toml
[model]
pretrained_model_name_or_path = "stabilityai/stable-diffusion-xl-base-1.0"

[dataset]
resolution = 1024
enable_bucket = true
min_bucket_reso = 640
max_bucket_reso = 1536
bucket_reso_steps = 64

[training]
max_train_epochs = 10
learning_rate = 1e-4
unet_lr = 1e-4
text_encoder_lr = 5e-5
lr_scheduler = "cosine_with_restarts"
lr_warmup_steps = 100
optimizer_type = "AdamW8bit"
train_batch_size = 1
gradient_accumulation_steps = 4
mixed_precision = "bf16"
cache_latents = true
cache_text_encoder_outputs = true

[network]
network_module = "networks.lora"
network_dim = 32
network_alpha = 16

[regularization]
# Optional: use base SDXL generations as regularization images
# This prevents the LoRA from overfitting and forgetting general knowledge
```

**VRAM Requirements**:
- 12 GB VRAM: batch_size=1, gradient_accumulation=4, cache latents
- 16 GB VRAM: batch_size=2, gradient_accumulation=2
- 24 GB VRAM: batch_size=4, comfortable headroom

### Regularization Images (Optional but Recommended)

Generate 100-200 images from base SDXL with generic anime prompts (no cyberpunk). These serve as "what NOT to change" and prevent the LoRA from drifting the base model's general capabilities.

```bash
# Generate regularization images using ComfyUI or diffusers
# Prompt examples: "anime girl in a park", "anime boy reading", "anime landscape, mountains"
```

### Training Launch

```bash
# Using kohya-ss sd-scripts
accelerate launch sdxl_train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="dataset/processed" \
  --output_dir="output/cpanime_lora" \
  --output_name="cpanime_v1" \
  --resolution=1024 \
  --enable_bucket \
  --min_bucket_reso=640 \
  --max_bucket_reso=1536 \
  --network_module="networks.lora" \
  --network_dim=32 \
  --network_alpha=16 \
  --learning_rate=1e-4 \
  --unet_lr=1e-4 \
  --text_encoder_lr=5e-5 \
  --lr_scheduler="cosine_with_restarts" \
  --max_train_epochs=10 \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --optimizer_type="AdamW8bit" \
  --mixed_precision="bf16" \
  --cache_latents \
  --cache_text_encoder_outputs \
  --save_every_n_epochs=2 \
  --sample_every_n_epochs=2 \
  --sample_prompts="sample_prompts.txt"
```

### Post-Training Validation

1. Generate test images at various LoRA weights (0.5, 0.7, 0.8, 1.0)
2. Test with prompts that were NOT in the training captions
3. Verify style transfer works on diverse subjects (characters, environments, vehicles)
4. Check for overfitting: if outputs look like specific training images, reduce epochs or increase regularization
5. Compare checkpoints from different epochs to find the sweet spot

---

## Timeline Estimate

| Phase | Estimated Time |
|---|---|
| Phase 2: Image Acquisition | 2-4 hours (mostly extraction time) |
| Phase 3: Curation | 3-5 hours (manual review is slow) |
| Phase 4: Image Processing | 30-60 minutes (mostly automated) |
| Phase 5: Captioning | 3-5 hours (auto-caption + manual refinement) |
| Phase 6: Validation | 30-60 minutes |
| Phase 7: Training | 2-8 hours (depending on VRAM and dataset size) |
| **Total** | **~12-24 hours** |

The biggest time investment is manual curation (Phase 3) and caption refinement (Phase 5c). These are where dataset quality is actually determined.
