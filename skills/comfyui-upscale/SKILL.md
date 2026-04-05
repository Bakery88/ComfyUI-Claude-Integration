# Skill: ComfyUI Upscale

> Upscale images to higher resolution using model-based, latent, or tile-based methods. Selects the best approach based on VRAM, source resolution, and quality goals.

## When to Use

- User asks "Upscale this image" / "Make it higher resolution" / "Enhance this"
- Called by `comfyui-generation` when the user wants post-generation upscaling
- User wants to go from draft resolution to final output resolution

## Dependencies

- **comfyui-inventory**: Must verify upscale models, checkpoints, and nodes are available
- **comfyui-workflow-builder**: Uses workflow builder for node construction and validation

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `list_models` | Check available upscale models |
| `get_node_info` | Get details for upscale-related nodes |
| `build_node` | Construct upscale nodes |
| `validate_workflow` | Validate the upscale workflow |
| `run_workflow` | Execute the upscale pipeline |
| `get_image` | Retrieve the upscaled result |

## Procedure

### Step 1: Assess the Upscale Task

Determine from user request and source image:

1. **Source resolution**: What size is the input image?
2. **Target scale**: How much larger? (2x, 4x, or specific dimensions)
3. **Quality goal**: Fast preview vs. maximum quality
4. **VRAM budget**: Check inventory for available VRAM

### Step 2: Select Upscale Method

Use this decision tree:

```
What's the goal?
├── Fast preview / simple upscale
│   └── Model-Based Upscale (fastest, good quality)
│       ├── Available: 4x-UltraSharp, 4x-Foolhardy-Remacri
│       └── Fallback: any ESRGAN-based model in inventory
│
├── Maximum quality (photo or artwork)
│   ├── VRAM ≥ 24GB → SUPIR (best quality, very slow)
│   ├── VRAM ≥ 12GB → Latent Upscale (hires fix pattern)
│   └── VRAM < 12GB → Tile-Based Upscale (lower VRAM, good quality)
│
├── Large image (source > 1024px on any side)
│   └── Tile-Based Upscale (prevents VRAM overflow)
│
└── User specified method → Use that method
```

### Step 3: Build the Upscale Workflow

Select the appropriate pipeline pattern:

#### Method A: Model-Based Upscale (Simple)

```
Load Image → Upscale Model Loader → Image Upscale With Model → Save Image
```

| Node | Class Type | Key Inputs |
|---|---|---|
| Load Image | `LoadImage` | `image`: filename |
| Upscale Model Loader | `UpscaleModelLoader` | `model_name`: from inventory |
| Image Upscale With Model | `ImageUpscaleWithModel` | `upscale_model`: from loader, `image`: from load |
| Save Image | `SaveImage` | `filename_prefix`: descriptive name |

**Best for**: Quick 4x upscales, non-AI artwork, screenshots. No re-generation involved.

#### Method B: Latent Upscale (Hires Fix)

```
Load Image → VAE Encode → Upscale Latent → KSampler (low denoise) → VAE Decode → Save Image
```

Also needs: checkpoint loader, CLIP text encode (positive + negative) feeding the KSampler.

| Parameter | Recommended Value |
|---|---|
| Upscale method | `nearest-exact` or `bilinear` |
| Scale factor | 1.5x or 2x (not 4x — chain two 2x passes for 4x) |
| KSampler denoise | 0.3–0.5 (lower = more faithful to original) |
| Steps | 15–25 |
| CFG | Same as original generation |

**Best for**: AI-generated images where you want to add detail while upscaling. Requires the same checkpoint used for the original generation.

#### Method C: Tile-Based Upscale (Ultimate SD Upscale)

```
Load Image → Upscale Model Loader → [Ultimate SD Upscale node] → Save Image
```

The Ultimate SD Upscale node internally handles tiling, KSampling, and reassembly.

| Parameter | Recommended Value |
|---|---|
| Tile width | 512 (SD 1.5) or 768–1024 (SDXL) |
| Tile height | Same as width |
| Tile overlap | 64–128 pixels (higher = fewer seam artifacts) |
| Denoise | 0.2–0.4 |
| Upscale model | 4x-UltraSharp or similar |
| Seam fix | Enable if visible tile boundaries |

**Requires**: `UltimateSDUpscale` custom node (check inventory). If not installed, suggest ComfyUI Manager.

**Best for**: Large upscales (4x+) on limited VRAM. Processes image in chunks.

#### Method D: SUPIR Upscale

```
Load Image → SUPIR Model Loader → SUPIR Encode → SUPIR Sampler → SUPIR Decode → Save Image
```

| Parameter | Recommended Value |
|---|---|
| Model | SUPIR-v0Q (quality) or SUPIR-v0F (fidelity) |
| Steps | 20–50 |
| CFG | 3–5 |
| Scale | 2x–4x |
| VRAM required | 24GB+ |

**Requires**: SUPIR custom nodes + SUPIR model (~5GB download). Check inventory first.

**Best for**: Photorealistic upscaling with detail hallucination. Slow but highest quality.

### Step 4: VRAM Planning

| Method | Approximate VRAM |
|---|---|
| Model-based (ESRGAN) | 1–2GB |
| Latent upscale (SD 1.5) | 4–6GB |
| Latent upscale (SDXL) | 8–10GB |
| Tile-based (SD 1.5, 512px tiles) | 4–6GB |
| Tile-based (SDXL, 768px tiles) | 8–10GB |
| SUPIR | 24GB+ |

If VRAM is tight:
- Use model-based upscale (lowest VRAM)
- Reduce tile size for tile-based method
- Use `--lowvram` ComfyUI flag
- Chain two smaller upscales (2x → 2x) instead of one 4x

### Step 5: Validate and Execute

1. Build the workflow using `build_node` for each node
2. Call `validate_workflow` to check connections and inputs
3. Present the plan to the user (per authority matrix — requires confirmation to run)
4. Execute via `run_workflow`, monitor via `get_task`
5. Retrieve result via `get_image`

### Step 6: Assess Results

After upscaling, check for common issues:
- **Tile seams**: Increase overlap or enable seam fix
- **Over-sharpening**: Lower denoise in latent/tile method
- **Loss of detail**: Switch from model-based to latent or SUPIR
- **Artifacts introduced**: Lower denoise, try different upscale model
- **Too blurry**: Increase denoise slightly, or switch to SUPIR

Offer to re-run with adjusted parameters if the user isn't satisfied.

## Upscale Model Reference

| Model | Scale | Quality | Speed | Notes |
|---|---|---|---|---|
| 4x-UltraSharp | 4x | Very good | Fast | Best general-purpose ESRGAN |
| 4x-Foolhardy-Remacri | 4x | Very good | Fast | Good for diverse content |
| RealESRGAN_x4plus | 4x | Good | Fast | Reliable default |
| RealESRGAN_x4plus_anime | 4x | Good (anime) | Fast | Optimized for anime/illustration |
| SUPIR-v0Q | 2x–4x | Excellent | Very slow | Best quality, needs 24GB VRAM |
| SUPIR-v0F | 2x–4x | Excellent | Very slow | Better fidelity preservation |

Check inventory for which of these are actually installed before recommending.

## Offline Mode

| Step | Online | Offline |
|---|---|---|
| Check upscale models | `list_models` | Use cached inventory |
| Build workflow | `build_node` + `validate_workflow` | Build JSON manually, skip validation |
| Execute | `run_workflow` | Save to `workflows/upscale-{name}.json` |

In offline mode, build the workflow JSON and save to `workflows/` with a descriptive name. Include a `_comment` field noting it's unvalidated.
