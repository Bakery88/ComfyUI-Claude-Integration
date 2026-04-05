# Dataset Plan: Vintage Mechanical Keyboard LoRA

## Overview

End-to-end pipeline to prepare a training dataset for a LoRA that captures the "vintage mechanical keyboard" aesthetic: beige/cream cases, colorful keycaps, chunky retro form factors from the 1980s-90s.

**Target**: 80-150 high-quality, captioned images at 512x512 or 1024x1024 resolution (depending on base model).

---

## Phase 1: Image Acquisition

### 1A. Reddit Downloads (gallery-dl)

```bash
# Install gallery-dl
pip install gallery-dl

# Download from r/MechanicalKeyboards -- search for vintage content
gallery-dl "https://www.reddit.com/r/MechanicalKeyboards/search/?q=vintage&sort=top&t=all"
gallery-dl "https://www.reddit.com/r/MechanicalKeyboards/search/?q=beige+keyboard&sort=top&t=all"
gallery-dl "https://www.reddit.com/r/MechanicalKeyboards/search/?q=IBM+Model+M&sort=top&t=all"
gallery-dl "https://www.reddit.com/r/MechanicalKeyboards/search/?q=retro+keycaps&sort=top&t=all"

# Download from r/VintageComputing
gallery-dl "https://www.reddit.com/r/VintageComputing/search/?q=keyboard&sort=top&t=all"

# Configure output directory
# In ~/.config/gallery-dl/config.json:
# { "extractor": { "reddit": { "directory": ["raw_downloads/reddit/{subreddit}"] } } }
```

### 1B. Flickr Downloads (gallery-dl with CC filter)

```bash
# Download CC-licensed vintage keyboard photos from Flickr
gallery-dl "https://www.flickr.com/search/?text=vintage+mechanical+keyboard&license=4,5,6,9,10"
gallery-dl "https://www.flickr.com/search/?text=retro+beige+keyboard&license=4,5,6,9,10"
gallery-dl "https://www.flickr.com/search/?text=IBM+Model+M&license=4,5,6,9,10"
```

### 1C. Deskthority Wiki (wget)

```bash
# Download keyboard images from Deskthority wiki pages
# First, build a URL list from relevant category pages
wget -r -l 2 -A "*.jpg,*.png" -P raw_downloads/deskthority \
  "https://deskthority.net/wiki/Category:Keyboards_with_Cherry_MX_switches" \
  "https://deskthority.net/wiki/IBM_Model_M" \
  "https://deskthority.net/wiki/Cherry_G80-3000"

# Or use gallery-dl if it supports the site
gallery-dl "https://deskthority.net/wiki/IBM_Model_M"
```

### 1D. Video Frame Extraction (yt-dlp + ffmpeg)

```bash
# Install yt-dlp
pip install yt-dlp

# Download specific videos from Chyrosran22 (vintage keyboard reviews)
# Example: download a specific video at 1080p
yt-dlp -f "bestvideo[height<=1080]" -o "raw_downloads/video/%(channel)s/%(title)s.%(ext)s" \
  "https://www.youtube.com/watch?v=VIDEO_ID_HERE"

# Extract frames every 2 seconds (captures variety without redundancy)
ffmpeg -i "raw_downloads/video/input.mp4" \
  -vf "fps=0.5,select='gt(scene,0.3)'" \
  -vsync vfr \
  "raw_downloads/video_frames/frame_%04d.png"

# Scene-change detection extracts only visually distinct frames:
# - fps=0.5 samples every 2 seconds
# - select='gt(scene,0.3)' filters to frames with >30% visual change
# This avoids extracting hundreds of near-identical frames

# For batch processing multiple videos:
for video in raw_downloads/video/Chyrosran22/*.mp4; do
  basename=$(basename "$video" .mp4)
  mkdir -p "raw_downloads/video_frames/$basename"
  ffmpeg -i "$video" \
    -vf "fps=0.5,select='gt(scene,0.3)'" \
    -vsync vfr \
    "raw_downloads/video_frames/$basename/frame_%04d.png"
done
```

### 1E. Manual Collection

Some sources (ClickyKeyboards, eBay listings) are best collected manually:
1. Browse the source site
2. Right-click and save images that match the target aesthetic
3. Save to `raw_downloads/manual/`
4. Keep a simple text log of where each image came from

---

## Phase 2: Curation and Filtering

### 2A. Initial Sort (Manual Review)

Create the following directory structure:
```
dataset/
  raw_downloads/       # Everything from Phase 1
  curated/
    keep/              # Images that match the aesthetic
    maybe/             # Borderline images (review later)
    reject/            # Off-topic, poor quality, watermarked
```

**Keep criteria:**
- Subject is clearly a keyboard matching the target aesthetic (beige case, colorful keycaps)
- Resolution >= 512px on shortest side
- Acceptable lighting (not extremely dark or blown out)
- No heavy watermarks or overlaid text (small corner watermarks can sometimes be cropped out)
- No NSFW or irrelevant content in background

**Reject criteria:**
- Modern RGB keyboards with no retro aesthetic
- Blurry or extremely low resolution (<400px shortest side)
- Heavy watermarks covering the subject
- Duplicate or near-duplicate images
- Images where the keyboard is too small in the frame (<25% of image area)

### 2B. Deduplication

```bash
# Install image deduplication tools
pip install imagededup

# Python script for deduplication
python -c "
from imagededup.methods import PHash
phasher = PHash()
encodings = phasher.encode_images(image_dir='dataset/curated/keep/')
duplicates = phasher.find_duplicates(encoding_map=encodings, max_distance_threshold=10)

# Print groups of duplicates
for img, dups in duplicates.items():
    if dups:
        print(f'{img} -> duplicates: {dups}')
"
# Review the output and remove duplicates, keeping the highest-quality version
```

### 2C. Watermark/Overlay Check

Manually scan through the `keep/` folder in a fast image viewer (e.g., IrfanView, XnView) and move any watermarked images back to `reject/` or crop them if the watermark is in a corner and doesn't affect the subject.

---

## Phase 3: Image Processing

### 3A. Resolution and Aspect Ratio

For SDXL-based LoRA training (recommended):
- **Target resolution**: 1024x1024
- **Acceptable aspect ratios**: Square, 3:4, 4:3, 2:3, 3:2 (bucketed training handles this)
- **Minimum input resolution**: 768px on shortest side (upscaling smaller images introduces artifacts)

For SD 1.5-based LoRA training:
- **Target resolution**: 512x512

```bash
# Install processing tools
pip install Pillow

# Python script to resize and prepare images
python << 'PYEOF'
import os
from PIL import Image

INPUT_DIR = "dataset/curated/keep"
OUTPUT_DIR = "dataset/processed"
TARGET_SIZE = 1024  # Use 512 for SD 1.5
MIN_SIZE = 768      # Minimum shortest side before resize

os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
        continue
    
    img_path = os.path.join(INPUT_DIR, filename)
    img = Image.open(img_path)
    w, h = img.size
    
    # Skip images that are too small
    if min(w, h) < MIN_SIZE // 2:
        print(f"SKIP (too small): {filename} ({w}x{h})")
        continue
    
    # Resize so shortest side = TARGET_SIZE, maintaining aspect ratio
    if w < h:
        new_w = TARGET_SIZE
        new_h = int(h * (TARGET_SIZE / w))
    else:
        new_h = TARGET_SIZE
        new_w = int(w * (TARGET_SIZE / h))
    
    # Use LANCZOS for high-quality downscaling
    img = img.resize((new_w, new_h), Image.LANCZOS)
    
    # Center crop to make both dimensions multiples of 64 (for bucketed training)
    new_w = (new_w // 64) * 64
    new_h = (new_h // 64) * 64
    left = (img.width - new_w) // 2
    top = (img.height - new_h) // 2
    img = img.crop((left, top, left + new_w, top + new_h))
    
    # Save as PNG (lossless) or high-quality JPEG
    out_name = os.path.splitext(filename)[0] + ".png"
    img.save(os.path.join(OUTPUT_DIR, out_name))
    print(f"OK: {filename} ({w}x{h}) -> {out_name} ({new_w}x{new_h})")

PYEOF
```

### 3B. Color and Quality Normalization (Optional)

```bash
# Optional: normalize white balance across the dataset
# This is useful if images come from very different lighting conditions
# Use ImageMagick:
for img in dataset/processed/*.png; do
  convert "$img" -normalize -modulate 100,100,100 "$img"
done
```

Generally, AVOID heavy normalization for LoRA training -- you want the model to learn the natural variation in the aesthetic, including slightly yellowed vintage plastic vs. clean restored beige.

---

## Phase 4: Captioning

### 4A. Auto-Captioning with BLIP-2 or WD-Tagger

```bash
# Option A: Use the kohya-ss/sd-scripts built-in captioning
# (if using kohya for training)
python finetune/make_captions.py --batch_size 4 --max_data_loader_n_workers 2 \
  --caption_extention .txt \
  dataset/processed/

# Option B: Use WD14 tagger for booru-style tags (good for anime-style models)
python finetune/tag_images_by_wd14_tagger.py \
  --batch_size 4 \
  --caption_extention .txt \
  dataset/processed/

# Option C: Use BLIP-2 via transformers
python << 'PYEOF'
import os
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration
import torch

model_name = "Salesforce/blip2-opt-2.7b"
processor = Blip2Processor.from_pretrained(model_name)
model = Blip2ForConditionalGeneration.from_pretrained(model_name, torch_dtype=torch.float16)
model.to("cuda")

IMAGE_DIR = "dataset/processed"

for filename in sorted(os.listdir(IMAGE_DIR)):
    if not filename.endswith(".png"):
        continue
    img = Image.open(os.path.join(IMAGE_DIR, filename))
    inputs = processor(img, return_tensors="pt").to("cuda", torch.float16)
    out = model.generate(**inputs, max_new_tokens=100)
    caption = processor.decode(out[0], skip_special_tokens=True).strip()
    
    # Save caption as .txt file alongside the image
    txt_path = os.path.join(IMAGE_DIR, filename.replace(".png", ".txt"))
    with open(txt_path, "w") as f:
        f.write(caption)
    print(f"{filename}: {caption}")
PYEOF
```

### 4B. Caption Refinement (Manual Pass)

Auto-generated captions need manual review and refinement:

1. **Add the trigger word** at the start of every caption: `vintagekb` (or your chosen trigger)
2. **Add specific details** the auto-captioner misses:
   - Keyboard brand/model if recognizable
   - Switch type if visible
   - Keycap material/profile (PBT, ABS, SA, DSA, Cherry profile)
   - Color descriptions (beige, cream, ivory, battleship gray)
   - Layout (full-size, TKL, 60%)
3. **Remove hallucinated details** from auto-captions
4. **Ensure consistency** in terminology across all captions

### 4C. Caption Format

Use natural language captions (not tags) for SDXL/Flux LoRA training:

```
vintagekb, a vintage IBM Model M mechanical keyboard with beige case and white keycaps, buckling spring switches, full-size layout, coiled cable, on a wooden desk
```

For SD 1.5, booru-style tags can also work:

```
vintagekb, vintage keyboard, mechanical keyboard, beige case, colorful keycaps, IBM Model M, full-size layout, desk, retro computing
```

---

## Phase 5: Dataset Validation

### 5A. Consistency Checks

```bash
# Verify every image has a matching caption file
python << 'PYEOF'
import os

IMAGE_DIR = "dataset/processed"
images = {f for f in os.listdir(IMAGE_DIR) if f.endswith('.png')}
captions = {f for f in os.listdir(IMAGE_DIR) if f.endswith('.txt')}

img_basenames = {os.path.splitext(f)[0] for f in images}
cap_basenames = {os.path.splitext(f)[0] for f in captions}

missing_captions = img_basenames - cap_basenames
missing_images = cap_basenames - img_basenames

if missing_captions:
    print(f"WARNING: {len(missing_captions)} images missing captions:")
    for m in sorted(missing_captions):
        print(f"  {m}.png")

if missing_images:
    print(f"WARNING: {len(missing_images)} captions missing images:")
    for m in sorted(missing_images):
        print(f"  {m}.txt")

if not missing_captions and not missing_images:
    print(f"OK: {len(images)} images all have matching captions")
PYEOF
```

### 5B. Resolution Verification

```bash
python << 'PYEOF'
import os
from PIL import Image

IMAGE_DIR = "dataset/processed"
issues = []

for filename in sorted(os.listdir(IMAGE_DIR)):
    if not filename.endswith('.png'):
        continue
    img = Image.open(os.path.join(IMAGE_DIR, filename))
    w, h = img.size
    if w % 64 != 0 or h % 64 != 0:
        issues.append(f"NOT 64-aligned: {filename} ({w}x{h})")
    if min(w, h) < 512:
        issues.append(f"TOO SMALL: {filename} ({w}x{h})")

if issues:
    print(f"Found {len(issues)} issues:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("All images pass resolution checks")
PYEOF
```

### 5C. Caption Quality Audit

```bash
# Check that all captions contain the trigger word
python << 'PYEOF'
import os

IMAGE_DIR = "dataset/processed"
TRIGGER = "vintagekb"
issues = []

for filename in sorted(os.listdir(IMAGE_DIR)):
    if not filename.endswith('.txt'):
        continue
    with open(os.path.join(IMAGE_DIR, filename)) as f:
        caption = f.read().strip()
    if not caption.startswith(TRIGGER):
        issues.append(f"Missing trigger: {filename}: {caption[:60]}...")
    if len(caption) < 20:
        issues.append(f"Too short: {filename}: {caption}")
    if len(caption) > 300:
        issues.append(f"Too long: {filename}: {caption[:60]}...")

if issues:
    print(f"Found {len(issues)} caption issues:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("All captions pass quality checks")
PYEOF
```

---

## Phase 6: Dataset Report Generation

```bash
python << 'PYEOF'
import os, json
from PIL import Image
from collections import Counter
from datetime import datetime

IMAGE_DIR = "dataset/processed"
REPORT_PATH = "dataset/dataset-report.json"

images = sorted(f for f in os.listdir(IMAGE_DIR) if f.endswith('.png'))
captions = sorted(f for f in os.listdir(IMAGE_DIR) if f.endswith('.txt'))

resolutions = Counter()
total_pixels = 0
caption_lengths = []
trigger_count = 0
TRIGGER = "vintagekb"

for img_file in images:
    img = Image.open(os.path.join(IMAGE_DIR, img_file))
    w, h = img.size
    resolutions[f"{w}x{h}"] += 1
    total_pixels += w * h

for cap_file in captions:
    with open(os.path.join(IMAGE_DIR, cap_file)) as f:
        text = f.read().strip()
    caption_lengths.append(len(text))
    if text.startswith(TRIGGER):
        trigger_count += 1

report = {
    "generated": datetime.now().isoformat(),
    "total_images": len(images),
    "total_captions": len(captions),
    "matched_pairs": len(set(os.path.splitext(f)[0] for f in images) &
                         set(os.path.splitext(f)[0] for f in captions)),
    "resolutions": dict(resolutions.most_common()),
    "avg_caption_length": round(sum(caption_lengths) / max(len(caption_lengths), 1), 1),
    "trigger_word_coverage": f"{trigger_count}/{len(captions)}",
    "estimated_training_time_sdxl": f"{len(images) * 2}-{len(images) * 4} minutes (rough estimate, depends on hardware and steps)",
}

with open(REPORT_PATH, "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2))
PYEOF
```

---

## Phase 7: Handoff to Training

### Directory Structure for Kohya ss/sd-scripts

```
training_data/
  10_vintagekb/          # "10" = repeat count, "vintagekb" = concept name
    image001.png
    image001.txt
    image002.png
    image002.txt
    ...
  1_keyboard/            # (optional) regularization images of generic keyboards
    reg001.png
    reg001.txt
    ...
```

### Recommended Training Parameters (SDXL LoRA)

```bash
accelerate launch --num_cpu_threads_per_process 1 sdxl_train_network.py \
  --pretrained_model_name_or_path="stabilityai/stable-diffusion-xl-base-1.0" \
  --train_data_dir="training_data" \
  --output_dir="output/vintagekb_lora" \
  --output_name="vintagekb_v1" \
  --network_module=networks.lora \
  --network_dim=32 \
  --network_alpha=16 \
  --resolution=1024,1024 \
  --train_batch_size=1 \
  --learning_rate=1e-4 \
  --unet_lr=1e-4 \
  --text_encoder_lr=5e-5 \
  --max_train_epochs=10 \
  --save_every_n_epochs=2 \
  --mixed_precision="bf16" \
  --optimizer_type="AdamW8bit" \
  --cache_latents \
  --gradient_checkpointing \
  --bucket_reso_steps=64 \
  --enable_bucket \
  --min_bucket_reso=512 \
  --max_bucket_reso=1536 \
  --caption_extension=".txt" \
  --seed=42
```

### Key Training Notes

- **Repeat count**: With 100 images, `10_vintagekb` gives 1000 steps/epoch. 10 epochs = 10,000 steps total.
- **Regularization images**: Optional but recommended. Use 200-500 images of generic modern keyboards to prevent the LoRA from forgetting what a "normal" keyboard looks like.
- **Network dim 32**: Good balance for a style/aesthetic LoRA. Use 64-128 for more complex concepts.
- **Bucket training**: Enabled so you don't need to force all images to the same aspect ratio.
- **Monitor for overfitting**: Generate test images every 2 epochs. If the model starts producing identical outputs regardless of prompt, reduce epochs or learning rate.

---

## Summary Checklist

- [ ] Phase 1: Download images from all sources (target: 200-400 raw images)
- [ ] Phase 2: Curate to 80-150 high-quality images
- [ ] Phase 3: Resize and process to training resolution
- [ ] Phase 4: Caption all images (auto + manual refinement)
- [ ] Phase 5: Validate dataset (pairs, resolution, caption quality)
- [ ] Phase 6: Generate dataset report
- [ ] Phase 7: Organize into training directory structure and launch training
