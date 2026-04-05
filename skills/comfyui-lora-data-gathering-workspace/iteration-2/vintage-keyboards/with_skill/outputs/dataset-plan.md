# Dataset Plan: Vintage Mechanical Keyboard LoRA

## Target
- **Subject**: Vintage mechanical keyboards (1980s-90s retro aesthetic)
- **Base Model**: FLUX
- **Target Images**: 25-30
- **Resolution**: 1024x1024 (with aspect-ratio bucketing)
- **Trigger Word**: `vintage_kb`

## Collection Strategy
1. Pull 15-20 images from Tier A sources (Deskthority, r/MechanicalKeyboards) — sharp, well-lit product photography
2. Supplement with 8-10 from Tier B (eBay listings, Flickr, GeekHack) — adds model variety and context shots
3. Use Tier C video frames only if specific gaps remain (e.g., need more side-profile angles)

## Captioning
- **Mode**: Object (`vintage_kb, {context description}`)
- **Captioner**: Florence-2
- **Hygiene rules**: Strip "vintage", "retro", "aesthetic", "classic", "old-school" from auto-captions — the LoRA learns these qualities visually, describing them in captions is redundant and dilutes the trigger association

## Diversity Checklist
- [ ] At least 5 different keyboard models (IBM Model M, Apple Extended, Cherry G80, Commodore, etc.)
- [ ] Mix of angles: top-down, side-profile, 3/4 angle, close-up detail shots
- [ ] Both isolated product shots and in-context desk setups
- [ ] Color variety: beige, grey, off-white cases; multiple keycap colorways
- [ ] Scale range: full board shots and zoomed-in key/switch detail

## Gap Analysis
- **Risk**: Over-representation of IBM Model M (most photographed vintage board). Mitigation: cap Model M at 6-8 images, actively seek underrepresented models.
- **Risk**: Angle bias toward top-down hero shots. Mitigation: specifically search for "side profile" and "detail" shots.
- **Iteration plan**: After first pass, check model diversity. If any single keyboard brand >40% of dataset, loop back for targeted searches of underrepresented brands.

## Training Parameters
- FLUX LoRA with AI-Toolkit
- Network rank: 16-32
- Target: 1000-1500 steps
- Resolution: 1024 with bucketing

## Next Steps
Dataset feeds into `comfyui-lora-training` skill. Say: "Train a LoRA using the vintage-keyboards dataset"
