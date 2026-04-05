# Dataset Plan: Vintage Keyboard LoRA (Baseline)

## Target
- **Subject**: Vintage mechanical keyboards, retro beige aesthetic
- **Base Model**: SDXL
- **Target Images**: 20-30
- **Resolution**: 1024x1024

## Steps
1. Download images from Reddit, Deskthority, eBay
2. Filter for quality — minimum 512px, sharp, well-lit
3. Remove duplicates
4. Resize to 1024x1024
5. Caption each image with a trigger word + description

## Captioning
- Trigger word: `vintage_keyboard`
- Format: trigger word followed by description of the keyboard and scene

## Training Parameters
- SDXL LoRA with Kohya_ss
- Network rank: 32
- Learning rate: 1e-4
- Epochs: 10
