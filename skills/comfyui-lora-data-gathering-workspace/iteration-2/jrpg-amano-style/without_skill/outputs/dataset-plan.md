# Dataset Plan: Amano JRPG Art Style LoRA (Baseline)

## Target
- **Subject**: Yoshitaka Amano JRPG watercolor art
- **Base Model**: FLUX
- **Target Images**: 25-30
- **Resolution**: 1024x1024

## Steps
1. Search Final Fantasy wiki for concept art galleries
2. Browse ArtStation and DeviantArt for fan studies
3. Collect from Pinterest boards
4. Filter for quality and consistency
5. Resize and crop to 1024px
6. Auto-caption with Florence-2

## Captioning
- Trigger word: `amano_style`
- Natural language captions from Florence-2

## Training Parameters
- FLUX LoRA with AI-Toolkit
- Network rank: 32
- Target: 1500 steps
- Resolution: 1024
