# Skill: ComfyUI Face ID

> Preserve or transfer facial identity across generated images. Select the best method based on quality requirements, available models, and VRAM.

## When to Use

- User asks "Keep the same face" / "Use this person's face" / "Generate with my face"
- User wants consistent character identity across multiple images
- User provides a face reference photo and wants it used in a generation

## Dependencies

- **comfyui-inventory**: Must verify face-related models and nodes are available
- **comfyui-workflow-builder**: Uses workflow builder for node construction
- **comfyui-prompt-engineer**: May need prompt crafting for the target scene

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `list_models` | Check for face-related models (IP-Adapter, InsightFace, etc.) |
| `list_nodes` | Verify face-related custom nodes are installed |
| `get_node_info` | Get inputs for face ID nodes |
| `build_node` | Construct face ID pipeline nodes |
| `validate_workflow` | Validate the complete workflow |

## Procedure

### Step 1: Assess Requirements

Determine:
1. **Reference image(s)**: How many face reference images does the user have?
2. **Task type**: Face swap into existing image vs. generate new image with face vs. consistent character across batch
3. **Quality priority**: Speed vs. likeness accuracy
4. **VRAM budget**: Check inventory

### Step 2: Select Method

Methods ranked by quality (best to worst). Use the highest-quality method the user's setup supports:

```
Which method to use?
├── VRAM ≥ 24GB + InfiniteYou nodes installed
│   └── InfiniteYou (best likeness, newest)
│
├── FLUX checkpoint + FLUX Kontext available
│   └── FLUX Kontext (native FLUX face transfer)
│
├── VRAM ≥ 16GB + PuLID nodes installed
│   └── PuLID Flux 2 (high quality FLUX face ID)
│
├── IP-Adapter FaceID nodes installed
│   ├── FLUX IP-Adapter → use if base model is FLUX
│   ├── SDXL IP-Adapter FaceID → use if base model is SDXL
│   └── SD 1.5 IP-Adapter FaceID → use if base model is SD 1.5
│
├── InstantID nodes installed (SDXL only)
│   └── InstantID (good quality, SDXL architecture only)
│
└── ReActor nodes installed
    └── ReActor (face swap, fastest, lowest quality)
```

### Step 3: Check Prerequisites

Each method has specific requirements. **Verify all are present in inventory before proceeding.**

#### InfiniteYou
- **Nodes**: `InfiniteYou` custom node pack
- **Models**: InfiniteYou model, InsightFace buffalo_l
- **VRAM**: 24GB+
- **Architecture**: FLUX

#### FLUX Kontext
- **Nodes**: Standard FLUX nodes (or Kontext-specific nodes)
- **Models**: FLUX Kontext checkpoint
- **VRAM**: 16–24GB
- **Architecture**: FLUX

#### PuLID Flux 2
- **Nodes**: `PuLID` custom node pack
- **Models**: PuLID FLUX model, EVA-CLIP, InsightFace antelopev2
- **VRAM**: 16GB+
- **Architecture**: FLUX

#### IP-Adapter FaceID
- **Nodes**: `IPAdapter` or `IPAdapterPlus` custom nodes
- **Models**: IP-Adapter FaceID model (architecture-specific), InsightFace buffalo_l or antelopev2
- **VRAM**: 10–16GB (varies by architecture)
- **Architecture**: SD 1.5, SDXL, or FLUX (model must match)

#### InstantID
- **Nodes**: `InstantID` custom node pack
- **Models**: InstantID model, InsightFace antelopev2
- **VRAM**: 12–16GB
- **Architecture**: SDXL only

#### ReActor
- **Nodes**: `ReActor` custom node pack
- **Models**: inswapper_128 model, InsightFace buffalo_l
- **VRAM**: 6–8GB (lightweight)
- **Architecture**: Any (post-processing face swap)

If the user is missing requirements, tell them what to install and suggest `get_download_url` for models or ComfyUI Manager for nodes.

### Step 4: Build the Pipeline

#### IP-Adapter FaceID Pipeline (most common)

```
[1] LoadImage (face reference)
[2] IPAdapterFaceID loader (load IP-Adapter FaceID model + InsightFace)
[3] IPAdapterApplyFaceID
      inputs: model (from checkpoint loader), image [1], ipadapter [2]
      outputs: model → feeds to KSampler
[4] Standard txt2img pipeline using the modified model from [3]
```

Key parameters:

| Parameter | Description | Recommended |
|---|---|---|
| `weight` | Face likeness strength | 0.7–1.0 (higher = more like reference) |
| `weight_type` | How weight is applied | `linear` or `ease in-out` |
| `start_at` | When to start applying | 0.0 |
| `end_at` | When to stop applying | 1.0 |
| `noise` | Variation noise | 0.0–0.3 (adds variation while keeping likeness) |

#### InstantID Pipeline

```
[1] LoadImage (face reference)
[2] InstantID Model Loader
[3] InsightFace Loader (antelopev2)
[4] Apply InstantID
      inputs: model, instantid_model [2], insightface [3], image [1],
              positive conditioning, negative conditioning
      outputs: model, positive, negative → feed to KSampler
```

Key parameters:

| Parameter | Recommended |
|---|---|
| `weight` | 0.8–1.0 |
| `start_at` | 0.0 |
| `end_at` | 1.0 |

#### ReActor Pipeline (Face Swap)

```
[1] Standard generation pipeline → produces output image
[2] LoadImage (face reference)
[3] ReActor Face Swap
      inputs: source_image [2], input_image [from generation output]
      outputs: swapped image → Save Image
```

ReActor is a post-processing step — it runs after the base image is generated, then swaps the face.

Key parameters:

| Parameter | Recommended |
|---|---|
| `face_restore_model` | CodeFormer or GFPGAN |
| `face_restore_visibility` | 0.5–1.0 |
| `codeformer_weight` | 0.5–0.7 |

### Step 5: Face Detail Restoration

For all methods, consider adding face restoration as a final step:

```
Generated Image → FaceDetailer → Save Image
```

Or use standalone face restoration:

| Node | Purpose | Quality |
|---|---|---|
| `FaceDetailer` | Detect faces → re-generate face region at high detail | Best (uses inpainting) |
| `FaceRestoreWithModel` (CodeFormer) | Neural face restoration | Good |
| `FaceRestoreWithModel` (GFPGAN) | GAN-based face restoration | Good (sometimes over-smooths) |

**FaceDetailer** is the best option as it re-generates the face area using inpainting, preserving style consistency. It requires a face detection model (e.g., `bbox/face_yolov8m.pt`) and an inpainting-capable checkpoint.

### Step 6: Validate and Execute

1. Build all nodes using `build_node`
2. Wire connections per the selected pipeline pattern
3. `validate_workflow` to check for errors
4. Present plan including method, reference image, and expected quality to user
5. Execute and retrieve result

### Step 7: Assess Results

| Issue | Likely Cause | Fix |
|---|---|---|
| Face doesn't match reference | Weight too low | Increase weight to 0.9–1.0 |
| Face looks pasted on / unnatural | Weight too high or style mismatch | Lower weight to 0.6–0.8; match art style in prompt |
| Distorted facial features | Bad face detection | Try different reference photo (frontal, well-lit, single face) |
| Multiple faces, wrong one changed | Face index wrong | Set face index to target correct face |
| Blurry face | Low resolution generation | Add FaceDetailer as post-processing step |
| Inconsistent across batch | Seed/noise variation | Use lower noise parameter; fix seed for consistency |

## Reference Image Guidelines

For best results, advise the user:

1. **Frontal or 3/4 view** — extreme angles reduce accuracy
2. **Good lighting** — even lighting on the face, no harsh shadows
3. **Single face** — avoid group photos as the reference
4. **Clear and sharp** — no blur, no occlusion (sunglasses, masks)
5. **Neutral expression works best** — extreme expressions may transfer oddly
6. **Resolution**: At least 512x512 face area
7. **Multiple references** (if supported): 3–5 photos from different angles improves likeness for methods that support multi-reference (IP-Adapter, PuLID)

## Consistent Character Across Multiple Images

For generating multiple images with the same character:

1. Generate the first image with face ID method
2. Use the **same reference image** and **same weight/settings** for subsequent generations
3. Fix the face-related parameters, only change pose/scene via prompt
4. Use FaceDetailer on each output for consistent quality
5. If using IP-Adapter: keep `noise` at 0.0 for maximum consistency

## Offline Mode

| Step | Online | Offline |
|---|---|---|
| Check face models | `list_models` | Use cached inventory |
| Check face nodes | `list_nodes` | Use cached inventory |
| Build workflow | `build_node` + `validate_workflow` | Build JSON manually, skip validation |
| Execute | `run_workflow` | Save to `workflows/faceid-{name}.json` |
