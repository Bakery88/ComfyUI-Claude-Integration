# Dataset Plan: Amano JRPG Watercolor Style LoRA

## Configuration

| Parameter | Value | Rationale |
|---|---|---|
| **Trigger word** | `amanostyle` | Unique, no collision with existing tokens |
| **Captioning mode** | `style` | We want the LoRA to learn the artistic style, not specific subjects |
| **Target resolution** | 1024px | FLUX native resolution |
| **Target image count** | 25-30 | Sweet spot for style LoRAs — enough variety without dilution |
| **Captioner** | Florence-2 | Best for natural language descriptions of art content |
| **Base model** | FLUX | User's target architecture |

## Collection Strategy

### Phase 1: Web Download
1. Crawl Final Fantasy Wiki Amano artwork category — extract direct image URLs
2. Download from Internet Archive art book scans — select watercolor/ink pieces only
3. Pull from Artnet gallery — high-quality professional photos

```bash
python scripts/download_images.py \
  --urls-file sources.json \
  --output-dir datasets/amano-jrpg-style/raw/ \
  --min-resolution 512
```

### Phase 2: Video Frame Extraction
Extract frames from YouTube "Art of Final Fantasy" compilations:

```bash
yt-dlp -f "bestvideo[height>=720]" -o "datasets/amano-jrpg-style/video/%(title)s.%(ext)s" "{video_url}"

python scripts/extract_frames.py \
  --video-dir datasets/amano-jrpg-style/video/ \
  --output-dir datasets/amano-jrpg-style/raw/ \
  --interval 3.0 \
  --min-resolution 512 \
  --dedupe-threshold 0.95
```

Use 3-second intervals since art compilation videos change images frequently.

### Phase 3: Curation Criteria
- **Include**: Watercolor/ink illustrations, concept art, character designs in Amano's classic style
- **Exclude**: 3D collaborations, digital-only later works, sketches/pencil-only pieces, heavily cropped images, images with visible book binding or page creases
- **Watch for**: Duplicate images across sources (art book scans + wiki may overlap)

### Phase 4: Processing

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/amano-jrpg-style/raw/ \
  --output-dir datasets/amano-jrpg-style/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png
```

### Phase 5: Captioning

```bash
python scripts/auto_caption.py \
  --image-dir datasets/amano-jrpg-style/processed/ \
  --trigger-word "amanostyle" \
  --mode style \
  --captioner florence2
```

### Phase 6: Hand-off
Dataset ready at `datasets/amano-jrpg-style/processed/`. To start training:
> "Train a LoRA using the amano-jrpg-style dataset"

This invokes the `comfyui-lora-training` skill with the prepared dataset. Recommended training params for a style LoRA on FLUX:
- Rank: 16
- Learning rate: 4e-4
- Steps: 1000-1500
- Resolution: 1024
