# Dataset Plan: Cyberpunk Anime Style LoRA (90s Hand-Painted)

## Target
- **Subject**: Cyberpunk anime style (Ghost in the Shell / Akira era, hand-painted cel look)
- **Base Model**: SDXL
- **Target Images**: 25-30
- **Resolution**: 1024x1024 (with aspect-ratio bucketing)
- **Trigger Word**: `cpanime90s`

## Collection Strategy
1. Pull 15+ images from Tier A (Halcyon Realms, settei archives) — production art is the gold standard
2. Supplement with 10-12 from Tier B (Safebooru, ArtStation) — **strict filtering**: reject clean digital art, 3D renders, modern anime styles. Only keep hand-painted/cel-style work.
3. Use Tier C video frames to fill specific gaps (e.g., if dataset lacks interior scenes or daytime settings)

## Captioning
- **Mode**: Style (`cpanime90s style, {content description}`)
- **Captioner**: WD14 Tagger for character scenes, Florence-2 for backgrounds
- **Hygiene rules**: Strip "anime", "cyberpunk", "cel-shaded", "hand-painted", "retro anime", "80s style", "neon-lit" from auto-captions. These describe the style the LoRA is learning — including them in captions weakens the trigger word association.

## Diversity Checklist
- [ ] At least 5 distinct scene types (cityscape, interior, character portrait, mecha/vehicle, action scene)
- [ ] Both night scenes (majority) and day/twilight scenes (at least 3-4)
- [ ] Mix of wide establishing shots and medium/close compositions
- [ ] Include both character-focused and environment-focused images
- [ ] Color range: neon-heavy scenes AND more subdued atmospheric pieces

## Gap Analysis
- **Risk**: Character art dominates online collections; background/environment art is rarer. Mitigation: prioritize settei archives which specialize in background art.
- **Risk**: Style drift from modern fan art that uses clean digital techniques. Mitigation: visual inspection of each Tier B source, reject anything that looks digitally rendered.
- **Risk**: Night-scene bias. Almost all cyberpunk anime art is nighttime. Include at least 3 daytime/interior scenes to teach the style independent of lighting.
- **Iteration plan**: After first curation pass, check: (1) background vs character ratio — aim for at least 40% backgrounds, (2) night vs day ratio — aim for at least 15% non-night. If either fails, loop back for targeted searches.

## Training Parameters
- SDXL LoRA with Kohya_ss
- Network rank: 32
- Epochs: 10
- Resolution: 1024 with bucketing

## Next Steps
Dataset feeds into `comfyui-lora-training` skill. Say: "Train a LoRA using the cyberpunk-anime dataset"
