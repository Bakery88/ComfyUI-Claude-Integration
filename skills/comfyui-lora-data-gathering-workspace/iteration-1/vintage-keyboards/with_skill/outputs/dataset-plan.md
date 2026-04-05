# Dataset Plan: Vintage Mechanical Keyboard LoRA

## Configuration

| Parameter | Value | Rationale |
|---|---|---|
| **Trigger word** | `vtgkbd` | Short, unique, no collision with existing tokens |
| **Captioning mode** | `object` | We want the LoRA to learn what vintage keyboards look like |
| **Target resolution** | 1024px | SDXL native resolution |
| **Target image count** | 25-30 | Enough variety across models without over-representing one board |
| **Captioner** | Florence-2 | Good at describing physical objects and their properties |
| **Base model** | SDXL | User's target architecture |

## Collection Strategy

### Phase 1: Web Download
1. Crawl Deskthority wiki pages for IBM Model M, Apple Extended Keyboard II, Commodore 64, etc.
2. Download from ClickyKeyboards product pages
3. Selectively grab high-quality eBay listing photos

```bash
python scripts/download_images.py \
  --urls-file sources.json \
  --output-dir datasets/vintage-keyboards/raw/ \
  --min-resolution 512
```

### Phase 2: Video Frame Extraction
Extract frames from keyboard collection tour videos and restoration videos:

```bash
yt-dlp -f "bestvideo[height>=720]" -o "datasets/vintage-keyboards/video/%(title)s.%(ext)s" "{video_url}"

python scripts/extract_frames.py \
  --video-dir datasets/vintage-keyboards/video/ \
  --output-dir datasets/vintage-keyboards/raw/ \
  --interval 5.0 \
  --min-resolution 512 \
  --dedupe-threshold 0.95
```

Use 5-second intervals — collection tours linger on each board.

### Phase 3: Curation Criteria
- **Include**: Full keyboard shots, close-ups of keycaps, angled views showing profile, keyboards on desks
- **Exclude**: Modern RGB keyboards, laptop keyboards, keyboards that aren't beige/retro styled, extreme close-ups of single switches, blurry photos
- **Variety needed**: Different keyboard models (IBM, Apple, Commodore, etc.), different angles (top-down, 3/4, side profile), different contexts (desk setup, isolated product shot)

### Phase 4: Processing

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/vintage-keyboards/raw/ \
  --output-dir datasets/vintage-keyboards/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png
```

### Phase 5: Captioning

```bash
python scripts/auto_caption.py \
  --image-dir datasets/vintage-keyboards/processed/ \
  --trigger-word "vtgkbd" \
  --mode object \
  --captioner florence2
```

### Phase 6: Hand-off
Dataset ready at `datasets/vintage-keyboards/processed/`. To start training:
> "Train a LoRA using the vintage-keyboards dataset"

Recommended SDXL LoRA training params for an object:
- Network rank: 32
- Learning rate: 1e-4 (unet), 5e-5 (text encoder)
- Epochs: 10
- Resolution: 1024
