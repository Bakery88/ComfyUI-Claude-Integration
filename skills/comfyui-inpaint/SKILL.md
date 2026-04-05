# Skill: ComfyUI Inpaint

> Edit specific regions of an image or extend image boundaries. Handles mask creation guidance, architecture-specific inpainting workflows, and iterative refinement.

## When to Use

- User asks "Fix this part of the image" / "Replace the background" / "Remove this object"
- User asks "Extend the image" / "Make it wider" / "Outpaint"
- User wants to modify a specific region while keeping the rest unchanged
- Called by `comfyui-generation` for targeted image editing

## Dependencies

- **comfyui-inventory**: Must verify inpainting models and nodes are available
- **comfyui-workflow-builder**: Uses workflow builder for node construction
- **comfyui-prompt-engineer**: Prompt the replacement content appropriately

## MCP Tools Used

| Tool | Purpose |
|---|---|
| `list_models` | Check for inpainting-specific checkpoints |
| `list_nodes` | Verify mask and inpainting nodes are installed |
| `get_node_info` | Get details for inpainting nodes |
| `build_node` | Construct inpainting pipeline nodes |
| `validate_workflow` | Validate the complete workflow |
| `run_workflow` | Execute the inpainting pipeline |
| `get_image` | Retrieve the inpainted result |

## Procedure

### Step 1: Understand the Edit

Determine:
1. **Edit type**: Inpainting (replace region) vs. outpainting (extend boundaries)
2. **What to change**: What should the masked region become?
3. **What to keep**: What parts of the image must remain untouched?
4. **Source image**: Does the user have the image loaded in ComfyUI?

### Step 2: Mask Strategy

The user needs a mask — a black and white image where **white = region to edit** and **black = region to keep**.

#### Mask Creation Methods

| Method | How | Best For |
|---|---|---|
| **Manual in ComfyUI** | Use ComfyUI's built-in mask editor (right-click image → Open in MaskEditor) | Precise control, complex shapes |
| **SAM (Segment Anything)** | Use `SAMModelLoader` + `SAMSegment` nodes | Object-based selection ("remove the car") |
| **GroundingDINO + SAM** | Text-guided segmentation: describe what to mask | "Mask the person" without manual drawing |
| **Solid color mask** | Create in image editor, load as mask | Simple rectangular regions |
| **Inverted mask** | Invert existing mask to edit everything EXCEPT a region | Keep subject, change background |

#### SAM Auto-Mask Pipeline

```
[1] LoadImage (source image)
[2] SAMModelLoader (load SAM model)
[3] GroundingDINOModelLoader (load GroundingDINO model)
[4] GroundingDINOSAMSegment
      inputs: image [1], sam_model [2], grounding_dino_model [3],
              prompt: "the object to select"
      outputs: mask → use in inpainting pipeline
```

**Requires**: `ComfyUI-segment-anything` or similar SAM nodes. Check inventory.

### Step 3: Select Inpainting Approach

```
What's the edit?
├── Replace a region (inpainting)
│   ├── Inpainting-specific checkpoint available
│   │   └── Use inpainting model (best quality)
│   └── No inpainting checkpoint
│       └── Use standard checkpoint with SetLatentNoiseMask (good quality)
│
├── Extend image boundaries (outpainting)
│   ├── Pad image → create mask for padded region → inpaint
│   └── Use outpainting-specific nodes if available
│
└── Remove object (leave background)
    └── Inpaint with prompt describing the background that should fill in
```

### Step 4: Build the Inpainting Workflow

#### Method A: Inpainting with Dedicated Model

```
[1] LoadImage (source image)
[2] LoadImage (mask — or generate via SAM)
[3] CheckpointLoaderSimple (inpainting checkpoint)
[4] VAEEncodeForInpaint
      inputs: image [1], mask [2], vae (from [3])
      grow_mask_by: 8 (pixels — feather the mask edge)
[5] CLIPTextEncode (positive — describe what should fill the masked area)
[6] CLIPTextEncode (negative)
[7] KSampler
      inputs: model [3], positive [5], negative [6], latent_image [4]
      denoise: 0.8–1.0 (see denoise guide below)
[8] VAEDecode → [9] SaveImage
```

#### Method B: Inpainting with Standard Model

```
[1] LoadImage (source image)
[2] LoadImage (mask)
[3] CheckpointLoaderSimple (standard checkpoint)
[4] VAEEncode (encode source image)
[5] SetLatentNoiseMask
      inputs: latent [4], mask [2]
[6] CLIPTextEncode (positive) → [7] CLIPTextEncode (negative)
[8] KSampler
      inputs: model [3], positive [6], negative [7], latent_image [5]
      denoise: 0.5–0.8
[9] VAEDecode → [10] SaveImage
```

#### Method C: Outpainting (Image Extension)

```
[1] LoadImage (source image)
[2] ImagePadForOutpaint (or PadImageForOutpainting)
      inputs: image [1], left/right/top/bottom: pixels to extend
      outputs: padded image, mask (auto-generated for new regions)
[3] VAEEncodeForInpaint
      inputs: padded_image [2], mask [2]
[4–8] Same as inpainting pipeline from KSampler onward
```

Prompt should describe the full scene including the original content and what should extend beyond.

### Step 5: Denoise Strength Guide

Denoise strength is the most critical parameter for inpainting quality:

| Denoise | Effect | Use When |
|---|---|---|
| **0.2–0.4** | Subtle changes, preserves most detail | Color correction, minor touch-ups |
| **0.4–0.6** | Moderate changes, blends well | Texture changes, material swaps |
| **0.6–0.8** | Significant changes, some original structure preserved | Object replacement (similar shape) |
| **0.8–1.0** | Full replacement, minimal influence from original | Complete region replacement, outpainting |

**Rule of thumb**: The more different the new content is from the original, the higher the denoise should be.

### Step 6: Architecture-Specific Inpainting

#### SD 1.5 Inpainting
- Dedicated model: `sd-v1-5-inpainting.ckpt` (or similar)
- Resolution: 512x512
- Works well with `VAEEncodeForInpaint`
- Most mature inpainting pipeline

#### SDXL Inpainting
- Dedicated model: Look for `sdxl-inpainting` or `sdxl_inpaint` in inventory
- Resolution: 1024x1024
- Fewer dedicated inpainting checkpoints — standard SDXL + `SetLatentNoiseMask` works well
- Use `grow_mask_by: 12–16` for smoother blending

#### FLUX Inpainting
- Dedicated model: FLUX Fill / FLUX Inpainting models
- Resolution: 1024x1024
- May require specific FLUX inpainting nodes (check inventory)
- Natural language prompt — no negative prompt needed
- CFG: 3.5 (standard FLUX)
- If no FLUX inpainting model, use standard FLUX + `SetLatentNoiseMask` with denoise 0.6–0.8

### Step 7: Validate and Execute

1. Build all nodes using `build_node`
2. Wire connections per selected pipeline
3. `validate_workflow` to check for errors
4. Present plan to user:
   ```
   Ready to inpaint:
   - Source: [image name]
   - Mask: [how mask was created]
   - Edit: [what will be changed]
   - Model: [checkpoint]
   - Denoise: [value]
   
   Shall I run this?
   ```
5. Execute and retrieve result

### Step 8: Iterative Refinement

Inpainting often requires multiple passes. After each result:

| Issue | Fix |
|---|---|
| Edited region doesn't blend | Lower denoise (0.4–0.6); increase `grow_mask_by` |
| New content doesn't match style | Use same checkpoint as original; match prompt style |
| Edges visible | Increase mask feathering; increase overlap region |
| Wrong content generated | Refine prompt; be more specific about what should appear |
| Result is blurry | Increase denoise; increase steps; ensure resolution matches model |
| Seam between edited and original | Grow mask to overlap more with original; run a second pass with lower denoise |

**Multi-pass refinement**: For complex edits, do a rough pass at high denoise (0.8–1.0) to establish content, then a refinement pass at low denoise (0.3–0.5) to blend edges.

## Common Inpainting Prompts

| Task | Prompt Strategy |
|---|---|
| Remove object | Describe the background that should fill in: "grassy field, natural lighting" |
| Replace background | Describe only the new background: "tropical beach, sunset, palm trees" |
| Change clothing | Describe the new clothing: "wearing a blue dress, silk fabric" |
| Fix face/hands | Describe the corrected feature: "detailed hands, five fingers, natural pose" |
| Add object | Describe the object in context: "a red coffee cup on the wooden table" |
| Extend image | Describe the full scene: "continuation of the forest landscape, trees, misty atmosphere" |

## Offline Mode

| Step | Online | Offline |
|---|---|---|
| Check inpainting models | `list_models` | Use cached inventory |
| Verify SAM/mask nodes | `list_nodes` | Use cached inventory |
| Build workflow | `build_node` + `validate_workflow` | Build JSON manually, skip validation |
| Execute | `run_workflow` | Save to `workflows/inpaint-{name}.json` |
