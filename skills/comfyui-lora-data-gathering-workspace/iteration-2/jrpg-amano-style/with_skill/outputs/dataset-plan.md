# Dataset Plan: Amano JRPG Art Style LoRA

## Target
- **Subject**: Yoshitaka Amano's watercolor JRPG illustration style
- **Base Model**: FLUX
- **Target Images**: 25-30
- **Resolution**: 1024x1024 (with aspect-ratio bucketing)
- **Trigger Word**: `amanoart`

## Collection Strategy
1. Pull 15+ images from Tier A sources (official gallery, FF wiki) — these form the style backbone
2. Supplement with 8-10 from Tier B (ArtStation studies, Safebooru) — adds subject variety
3. If gaps remain after curation, use Tier C video frames to fill specific holes

## Captioning
- **Mode**: Style (`amanoart style, {content description}`)
- **Captioner**: Florence-2
- **Hygiene rules**: Strip "watercolor", "painting", "illustration", "art nouveau", "ethereal" from auto-captions — the LoRA learns these visual qualities from pixels, not words

## Diversity Checklist
- [ ] At least 5 distinct subjects (characters, landscapes, group scenes, creatures, still life)
- [ ] Mix of close-up portraits and full-body/environment compositions
- [ ] Color range: include both muted palette pieces and vivid accent pieces
- [ ] Both finished illustrations and looser concept sketches

## Gap Analysis
- **Risk**: Dataset may skew toward FF character portraits. Mitigation: actively search for Amano's non-FF work (Sandman covers, fine art prints) and environment pieces.
- **Risk**: Color desaturation from poor scans. Mitigation: prefer Tier A sources with accurate reproduction.
- **Iteration plan**: After first pass curation, if >60% of images are single-character portraits, loop back and search specifically for landscapes and group compositions.

## Training Parameters
- FLUX LoRA with AI-Toolkit
- Network rank: 16-32
- Target: 1000-1500 steps
- Resolution: 1024 with bucketing

## Next Steps
Dataset feeds into `comfyui-lora-training` skill. Say: "Train a LoRA using the amano-jrpg dataset"
