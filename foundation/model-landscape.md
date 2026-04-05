# Model Landscape — Top Picks per Category

<!-- Updated: 2026-04-04 — review every 3 months -->

Quick reference for model selection. Verify availability against `state/inventory.json` before use.

## Image Generation (txt2img)

| Rank | Model | Best For | VRAM | Key Notes |
|---|---|---|---|---|
| 1 | **FLUX.2 [dev]** | Photorealism, multi-reference | 24GB+ | 32B params; natural language prompts, CFG 3.5 |
| 2 | **FLUX.1-dev** | Proven photorealism | 16GB+ | NVFP4/NVFP8 available |
| 3 | FLUX.2 [klein] | Fast generation, low VRAM | 12GB+ | Distilled, 4 steps |
| 4 | RealVisXL V5.0 | SDXL photorealism | 8GB+ | Fast, quality tags, CFG 7-9 |
| 5 | SD 1.5 variants | Legacy, huge LoRA ecosystem | 6GB+ | Tag-based prompts, CFG 7-11 |

## Identity Preservation

| Rank | Method | Best For | VRAM |
|---|---|---|---|
| 1 | InfiniteYou | Highest identity fidelity | 24GB |
| 2 | FLUX Kontext | Edit without retraining | 12-32GB |
| 3 | PuLID Flux 2 | FLUX.2 family | 24-40GB |
| 4 | InstantID | SDXL face swap (legacy) | 12GB |

## Inpainting / img2img

| Model | Best For | Notes |
|---|---|---|
| FLUX.2 [dev] inpaint | High-quality fills | Needs inpaint-specific checkpoint |
| SDXL inpainting | General inpainting | Widely supported |
| SD 1.5 inpainting | Legacy workflows | Largest community support |

## ControlNet / Guidance

| Model Family | Available Control Types |
|---|---|
| FLUX ControlNet | Canny, depth, pose (check inventory) |
| SDXL ControlNet | Canny, depth, pose, tile, inpaint |
| SD 1.5 ControlNet | Full suite (most mature ecosystem) |

## LoRA

| Training Tool | Best For | FLUX Support |
|---|---|---|
| Kohya ss | Gold standard, most configurable | Yes |
| Ostris AI Toolkit | Simple FLUX training | Yes |

## Video Generation

| Rank | Model | Best For | VRAM |
|---|---|---|---|
| 1 | LTX-2.3 | 4K, production quality | 24GB+ |
| 2 | Wan 2.6 | Reference-to-video, lip-sync | 24GB+ |
| 3 | FramePack | Long videos, low VRAM | 6GB+ |
| 4 | AnimateDiff V3 | Fast iteration, motion LoRAs | 8GB+ |

## Performance Optimization

| Tool | Speedup | VRAM Savings | Compatibility |
|---|---|---|---|
| NVFP4 (RTX 50 only) | 3x | 60% less | Requires PyTorch cu130 |
| NVFP8 (any NVIDIA) | 2x | 40% less | Broadly compatible |
| Nunchaku (SVDQuant) | 2-3x | 3.5x reduction | RTX 20+ series |
| WaveSpeed (FBCache) | Up to 2x | Minimal | Works with LoRA |

## Model Selection Decision Tree

```
User wants image generation:
├── Photorealistic? → FLUX.2 dev (24GB+) or FLUX.1-dev (16GB+)
├── Fast/iterative? → FLUX.2 klein (12GB+)
├── SDXL ecosystem (LoRAs, ControlNet)? → RealVisXL V5.0 (8GB+)
├── Low VRAM (<8GB)? → SD 1.5 variant
└── Identity preservation?
    ├── Highest fidelity → InfiniteYou
    ├── Iterative editing → FLUX Kontext
    └── FLUX family → PuLID Flux 2
```
