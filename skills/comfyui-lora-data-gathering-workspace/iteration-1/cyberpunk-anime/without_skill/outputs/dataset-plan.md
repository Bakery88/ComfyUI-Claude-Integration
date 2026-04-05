# Dataset Plan: Cyberpunk Anime LoRA (Baseline)

## Target
- **Subject**: Cyberpunk anime style (GITS, Akira)
- **Base Model**: SDXL
- **Target Images**: 30-40
- **Resolution**: 1024x1024

## Steps
1. Scrape Danbooru for cyberpunk + anime tagged images
2. Download production art from Halcyon Realms
3. Collect from Pinterest boards
4. Filter for quality and style consistency
5. Resize and crop to 1024px
6. Auto-caption with WD14 tagger

## Captioning
- Trigger word: `cyberpunk_anime_style`
- Tag-based captions from WD14

## Training Parameters
- SDXL LoRA with Kohya_ss
- Network rank: 32
- Epochs: 10
- Resolution: 1024
