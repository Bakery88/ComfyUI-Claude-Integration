# Dataset Plan: Cyberpunk Anime Style LoRA

## Configuration

| Parameter | Value | Rationale |
|---|---|---|
| **Trigger word** | `cybranime` | Short, unique, combines "cyberpunk" + "anime" |
| **Captioning mode** | `style` | We want the LoRA to learn the cyberpunk anime aesthetic |
| **Target resolution** | 1024px | SDXL native resolution (user specified SDXL) |
| **Target image count** | 30-35 | Style spans two major franchises + broader aesthetic — needs more variety |
| **Captioner** | WD14 Tagger | Better at anime-specific visual elements and tags |
| **Base model** | SDXL | User's target architecture |

## Collection Strategy

### Phase 1: Web Download
1. Crawl Halcyon Realms articles for Akira and GITS production art
2. Download from akira.ie cel documentation
3. Pull select images from Heritage Auctions listings

```bash
python scripts/download_images.py \
  --urls-file sources.json \
  --output-dir datasets/cyberpunk-anime/raw/ \
  --min-resolution 512
```

### Phase 2: Video Frame Extraction
Extract key frames from anime analysis videos and "making of" documentaries:

```bash
yt-dlp -f "bestvideo[height>=720]" -o "datasets/cyberpunk-anime/video/%(title)s.%(ext)s" "{video_url}"

python scripts/extract_frames.py \
  --video-dir datasets/cyberpunk-anime/video/ \
  --output-dir datasets/cyberpunk-anime/raw/ \
  --interval 3.0 \
  --min-resolution 512 \
  --dedupe-threshold 0.95
```

For actual anime footage (if extracting from the films directly), use 10-second intervals to avoid too many similar frames from the same scene.

### Phase 3: Curation Criteria
- **Include**: Background art, key animation frames, cityscape paintings, detailed mechanical designs, atmospheric scenes with neon lighting
- **Exclude**: Simple dialogue scenes, extreme close-ups of just faces, modern CG anime that doesn't match the hand-painted look, images with subtitles or UI overlays
- **Balance**: Aim for ~40% Akira, ~40% Ghost in the Shell, ~20% other cyberpunk anime (Bubblegum Crisis, Blade Runner: Black Lotus) for breadth
- **Style consistency**: Prefer hand-painted cel/gouache aesthetic over modern digital anime

### Phase 4: Processing

```bash
python scripts/prepare_dataset.py \
  --input-dir datasets/cyberpunk-anime/raw/ \
  --output-dir datasets/cyberpunk-anime/processed/ \
  --target-resolution 1024 \
  --crop-mode smart \
  --format png
```

### Phase 5: Captioning

```bash
python scripts/auto_caption.py \
  --image-dir datasets/cyberpunk-anime/processed/ \
  --trigger-word "cybranime" \
  --mode style \
  --captioner wd14
```

WD14 will produce tag-style captions good for anime. Review and supplement with scene descriptions where tags are too sparse.

### Phase 6: Hand-off
Dataset ready at `datasets/cyberpunk-anime/processed/`. To start training:
> "Train a LoRA using the cyberpunk-anime dataset"

Recommended SDXL LoRA training params for a style:
- Network rank: 32
- Learning rate: 1e-4 (unet), 5e-5 (text encoder)
- Epochs: 10
- Resolution: 1024
- Noise offset: 0.1 (helps with the high-contrast neon lighting in this style)
