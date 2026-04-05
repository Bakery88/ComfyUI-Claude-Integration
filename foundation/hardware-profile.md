# Hardware Profile

<!-- Updated: PENDING — run get_status to auto-detect -->

## Instructions

This file should be updated with your actual hardware after connecting to ComfyUI.
Run `get_status` via the MCP server to detect GPU and system info, then fill in the sections below.

## GPU

| Property | Value |
|---|---|
| Model | _detect via get_status_ |
| VRAM | _detect via get_status_ |
| Driver | _detect via get_status_ |
| CUDA Version | _detect via get_status_ |

## ComfyUI Instance

| Property | Value |
|---|---|
| URL | `http://localhost:8188` |
| Version | _detect via get_status_ |
| Launch Flags | _check ComfyUI startup args_ |

## VRAM Budget Guidelines

Use these thresholds for model selection and workflow planning:

| Available VRAM | Can Run | Optimization Needed |
|---|---|---|
| 24GB+ | Everything (FLUX FP16, Wan 14B, PuLID) | None |
| 16-24GB | FLUX (FP8/GGUF), SDXL, most video models | FP8 quantization |
| 12-16GB | FLUX Klein, SDXL, SD1.5, FramePack | `--lowvram`, FP8 |
| 8-12GB | SDXL (careful), SD1.5, AnimateDiff | `--lowvram`, smaller models |
| <8GB | SD1.5, FramePack (minimal) | `--lowvram --cpu-offload` |

## Performance Notes

- NVFP4 (RTX 50 series only): 3x faster, 60% less VRAM — requires PyTorch cu130
- NVFP8 (any NVIDIA): 2x faster, 40% less VRAM
- ComfyUI async offloading + pinned memory: ~40% faster on all NVIDIA GPUs (enabled by default since late 2025)
