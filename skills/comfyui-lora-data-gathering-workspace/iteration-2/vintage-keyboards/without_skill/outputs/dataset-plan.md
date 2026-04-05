# Dataset Plan: Vintage Keyboard LoRA (Baseline)

## Target
- **Subject**: Vintage mechanical keyboards
- **Base Model**: FLUX
- **Target Images**: 20-30
- **Resolution**: 1024x1024

## Steps
1. Browse Deskthority wiki for keyboard photos
2. Search Reddit for top vintage keyboard posts
3. Check eBay listings for product photos
4. Collect from Pinterest boards
5. Filter for quality and remove duplicates
6. Resize to 1024px
7. Auto-caption with Florence-2

## Captioning
- Trigger word: `vintage_keyboard`
- Natural language captions describing each keyboard

## Training Parameters
- FLUX LoRA with AI-Toolkit
- Network rank: 32
- Target: 1500 steps
- Resolution: 1024
